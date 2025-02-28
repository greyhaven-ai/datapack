"""
Email to MDP converter.

This module provides functions to convert email files (EML, MSG) to MDP format,
preserving headers, content, and attachments.
"""

import os
import io
import email
import datetime
import re
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
from email.header import decode_header
from email.utils import parsedate_to_datetime

try:
    import mailparser
    EMAIL_SUPPORT = True
except ImportError:
    EMAIL_SUPPORT = False

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date
from .utils import normalize_metadata

def _check_email_support():
    """
    Check if email parsing support is available.
    
    Raises:
        ImportError: If email parsing support is not available
    """
    if not EMAIL_SUPPORT:
        raise ImportError(
            "Email parsing support requires additional dependencies. "
            "Install with 'pip install datapack[converters]' or 'pip install mail-parser'"
        )

def _decode_header_value(value: str) -> str:
    """
    Decode an email header value.
    
    Args:
        value: The header value to decode
        
    Returns:
        The decoded header value
    """
    if not value:
        return ""
    
    decoded_parts = []
    for part, encoding in decode_header(value):
        if isinstance(part, bytes):
            if encoding:
                try:
                    decoded_parts.append(part.decode(encoding))
                except (UnicodeDecodeError, LookupError):
                    # Fallback to utf-8 if the specified encoding fails
                    try:
                        decoded_parts.append(part.decode('utf-8', errors='replace'))
                    except UnicodeDecodeError:
                        decoded_parts.append(part.decode('ascii', errors='replace'))
            else:
                try:
                    decoded_parts.append(part.decode('utf-8', errors='replace'))
                except UnicodeDecodeError:
                    decoded_parts.append(part.decode('ascii', errors='replace'))
        else:
            decoded_parts.append(part)
    
    return ''.join(decoded_parts)

def _extract_metadata_from_email(parsed_email: 'mailparser.MailParser') -> Dict[str, Any]:
    """
    Extract metadata from an email.
    
    Args:
        parsed_email: A parsed email object
        
    Returns:
        A dictionary of metadata
    """
    _check_email_support()
    
    metadata = {}
    
    # Extract basic email headers
    headers = parsed_email.headers
    
    # Extract subject as title
    if parsed_email.subject:
        metadata['title'] = parsed_email.subject
    
    # Extract sender as author
    if parsed_email.from_:
        from_values = parsed_email.from_
        if from_values:
            if isinstance(from_values, list) and len(from_values) > 0:
                from_value = from_values[0]
                if isinstance(from_value, dict):
                    name = from_value.get('name', '')
                    email_addr = from_value.get('email', '')
                    if name:
                        metadata['author'] = name
                    elif email_addr:
                        metadata['author'] = email_addr
                else:
                    metadata['author'] = str(from_value)
            else:
                metadata['author'] = str(from_values)
    
    # Extract date
    if parsed_email.date:
        try:
            metadata['created_at'] = format_date(parsed_email.date)
        except (ValueError, TypeError):
            # If parsing fails, try to format as string
            metadata['created_at'] = str(parsed_email.date)
    
    # Extract recipients
    recipients = []
    if parsed_email.to:
        for to in parsed_email.to:
            if isinstance(to, dict):
                if 'email' in to:
                    recipients.append(to['email'])
            else:
                recipients.append(str(to))
    
    if recipients:
        metadata['recipients'] = recipients
    
    # Extract CC recipients
    cc_recipients = []
    if parsed_email.cc:
        for cc in parsed_email.cc:
            if isinstance(cc, dict):
                if 'email' in cc:
                    cc_recipients.append(cc['email'])
            else:
                cc_recipients.append(str(cc))
    
    if cc_recipients:
        metadata['cc'] = cc_recipients
    
    # Extract message ID
    if 'message-id' in headers:
        metadata['message_id'] = headers['message-id']
    
    # Extract attachment info
    if parsed_email.attachments:
        attachments = []
        for attachment in parsed_email.attachments:
            attachments.append({
                'filename': attachment.get('filename', 'unknown'),
                'content_type': attachment.get('mail_content_type', 'application/octet-stream'),
                'size': len(attachment.get('payload', b''))
            })
        
        if attachments:
            metadata['attachments'] = attachments
    
    # Extract other useful headers
    for header_name in ['In-Reply-To', 'References', 'Reply-To', 'Return-Path', 'Importance', 'Priority']:
        if header_name.lower() in headers:
            metadata[header_name.lower().replace('-', '_')] = headers[header_name.lower()]
    
    # Normalize metadata to conform to MDP standards
    return normalize_metadata(metadata)

def _email_to_markdown(parsed_email: 'mailparser.MailParser') -> str:
    """
    Convert an email to markdown.
    
    Args:
        parsed_email: A parsed email object
        
    Returns:
        Markdown representation of the email
    """
    _check_email_support()
    
    content = []
    
    # Add email headers
    content.append("# " + (parsed_email.subject or "No Subject"))
    content.append("")
    
    # Add metadata section
    content.append("## Email Metadata")
    content.append("")
    
    # From
    if parsed_email.from_:
        from_values = parsed_email.from_
        if isinstance(from_values, list) and len(from_values) > 0:
            from_value = from_values[0]
            if isinstance(from_value, dict):
                name = from_value.get('name', '')
                email_addr = from_value.get('email', '')
                if name and email_addr:
                    content.append(f"**From:** {name} <{email_addr}>")
                elif email_addr:
                    content.append(f"**From:** {email_addr}")
            else:
                content.append(f"**From:** {from_value}")
        else:
            content.append(f"**From:** {from_values}")
    
    # To
    if parsed_email.to:
        to_str = []
        for to in parsed_email.to:
            if isinstance(to, dict):
                name = to.get('name', '')
                email_addr = to.get('email', '')
                if name and email_addr:
                    to_str.append(f"{name} <{email_addr}>")
                elif email_addr:
                    to_str.append(email_addr)
            else:
                to_str.append(str(to))
        
        if to_str:
            content.append(f"**To:** {', '.join(to_str)}")
    
    # CC
    if parsed_email.cc:
        cc_str = []
        for cc in parsed_email.cc:
            if isinstance(cc, dict):
                name = cc.get('name', '')
                email_addr = cc.get('email', '')
                if name and email_addr:
                    cc_str.append(f"{name} <{email_addr}>")
                elif email_addr:
                    cc_str.append(email_addr)
            else:
                cc_str.append(str(cc))
        
        if cc_str:
            content.append(f"**CC:** {', '.join(cc_str)}")
    
    # Date
    if parsed_email.date:
        content.append(f"**Date:** {parsed_email.date}")
    
    # Subject (again for completeness)
    if parsed_email.subject:
        content.append(f"**Subject:** {parsed_email.subject}")
    
    content.append("")
    
    # Add email body
    content.append("## Email Body")
    content.append("")
    
    # Try to get HTML body first, then plain text
    if parsed_email.text_html:
        # Use the first HTML part
        html_content = parsed_email.text_html[0] if isinstance(parsed_email.text_html, list) else parsed_email.text_html
        
        # Try to convert HTML to markdown
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            content.append(text)
        except ImportError:
            # If BeautifulSoup is not available, just use the HTML
            content.append("```html")
            content.append(html_content)
            content.append("```")
    elif parsed_email.text_plain:
        # Use the first plain text part
        text_content = parsed_email.text_plain[0] if isinstance(parsed_email.text_plain, list) else parsed_email.text_plain
        content.append(text_content)
    else:
        content.append("*No email body content found*")
    
    content.append("")
    
    # Add attachments section if there are any
    if parsed_email.attachments:
        content.append("## Attachments")
        content.append("")
        
        for i, attachment in enumerate(parsed_email.attachments, 1):
            filename = attachment.get('filename', 'unknown')
            content_type = attachment.get('mail_content_type', 'application/octet-stream')
            size = len(attachment.get('payload', b''))
            
            content.append(f"{i}. **{filename}** ({content_type}, {size} bytes)")
        
        content.append("")
    
    return '\n'.join(content)

def email_to_mdp(
    email_data: Union[str, Path, bytes, io.BytesIO], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True
) -> Document:
    """
    Convert email data to an MDP document.
    
    Args:
        email_data: Email data as a file path, bytes, or BytesIO object
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the email
        
    Returns:
        An MDP Document object
        
    Raises:
        ImportError: If email parsing support is not available
        ValueError: If email_data is invalid
    """
    _check_email_support()
    
    # Load the email data
    try:
        mail = mailparser.parse_from_file_obj(email_data) if isinstance(email_data, (io.BytesIO, bytes)) else mailparser.parse_from_file(email_data)
    except Exception as e:
        raise ValueError(f"Failed to parse email: {e}") from e
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata:
        doc_metadata = _extract_metadata_from_email(mail)
    
    # Override with provided metadata
    if metadata:
        # Normalize the provided metadata too
        normalized_metadata = normalize_metadata(metadata)
        doc_metadata.update(normalized_metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        # Try to use filename if available
        if isinstance(email_data, (str, Path)) and os.path.exists(email_data):
            filename = os.path.basename(email_data)
            base_name = os.path.splitext(filename)[0]
            doc_metadata["title"] = base_name.replace('_', ' ').replace('-', ' ').title()
        else:
            doc_metadata["title"] = "Converted Email"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "email",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.email_converter"
    }
    
    # Convert email to markdown
    content = _email_to_markdown(mail)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 