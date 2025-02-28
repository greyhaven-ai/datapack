"""
HTML to MDP converter.

This module provides functions to convert HTML data to MDP format,
preserving structure and metadata.
"""

import os
import re
import datetime
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import io

try:
    from bs4 import BeautifulSoup
    HTML_SUPPORT = True
except ImportError:
    HTML_SUPPORT = False

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date
from .utils import normalize_metadata

def _check_html_support():
    """
    Check if HTML support is available.
    
    Raises:
        ImportError: If HTML support is not available
    """
    if not HTML_SUPPORT:
        raise ImportError(
            "HTML support requires additional dependencies. "
            "Install with 'pip install datapack[converters]' or 'pip install beautifulsoup4'"
        )

def _extract_metadata_from_html(soup: 'BeautifulSoup') -> Dict[str, Any]:
    """
    Extract metadata from HTML content.
    
    Args:
        soup: BeautifulSoup object of the HTML content
        
    Returns:
        A dictionary of metadata
    """
    _check_html_support()
    
    metadata = {}
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        metadata['title'] = title_tag.string.strip()
    
    # Extract metadata from meta tags
    meta_mapping = {
        'description': ['description', 'og:description', 'twitter:description'],
        'author': ['author', 'og:author', 'twitter:creator', 'article:author'],
        'created_at': ['article:published_time', 'date', 'created', 'published_date'],
        'updated_at': ['article:modified_time', 'modified', 'updated_date'],
        'tags': ['keywords', 'article:tag', 'og:keywords']
    }
    
    for meta_key, possible_names in meta_mapping.items():
        for name in possible_names:
            # Try with name attribute
            meta_tag = soup.find('meta', attrs={'name': name})
            if not meta_tag:
                # Try with property attribute (for Open Graph)
                meta_tag = soup.find('meta', attrs={'property': name})
            
            if meta_tag and meta_tag.get('content'):
                content = meta_tag.get('content').strip()
                
                # Handle tags/keywords (comma-separated)
                if meta_key == 'tags' and ',' in content:
                    metadata[meta_key] = [tag.strip() for tag in content.split(',')]
                else:
                    metadata[meta_key] = content
                break
    
    # Format dates if needed
    for date_field in ["created_at", "updated_at"]:
        if date_field in metadata and isinstance(metadata[date_field], str):
            try:
                # Use the mdp format_date utility
                metadata[date_field] = format_date(metadata[date_field])
            except (ValueError, TypeError):
                # If parsing fails, keep as is
                pass
    
    # Extract other meta tags that might be useful as custom fields
    for meta_tag in soup.find_all('meta'):
        name = meta_tag.get('name') or meta_tag.get('property')
        if name and meta_tag.get('content'):
            # Skip already processed meta tags
            if any(name in names for _, names in meta_mapping.items()):
                continue
            
            # Add as custom field directly (will be normalized later)
            metadata[name.replace(':', '_')] = meta_tag.get('content').strip()
    
    # Normalize metadata to conform to MDP standards
    return normalize_metadata(metadata)

def _html_to_markdown(soup: 'BeautifulSoup', base_url: Optional[str] = None) -> str:
    """
    Convert HTML content to markdown.
    
    Args:
        soup: BeautifulSoup object of the HTML content
        base_url: Optional base URL for resolving relative links
        
    Returns:
        Markdown representation of the HTML content
    """
    _check_html_support()
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Process the main content
    content = []
    
    # Extract the main content (prefer article, main, or div with content-related classes)
    main_content = soup.find('article') or soup.find('main')
    if not main_content:
        for div in soup.find_all('div'):
            class_attr = div.get('class', [])
            if isinstance(class_attr, str):
                class_attr = [class_attr]
            
            # Look for content-related classes
            content_classes = ['content', 'article', 'post', 'entry', 'main']
            if any(c in ' '.join(class_attr).lower() for c in content_classes):
                main_content = div
                break
    
    # If no main content found, use body
    if not main_content:
        main_content = soup.body or soup
    
    # Process headings
    for i in range(1, 7):
        for heading in main_content.find_all(f'h{i}'):
            heading_text = heading.get_text().strip()
            if heading_text:
                # Add appropriate markdown heading
                content.append(f"{'#' * i} {heading_text}\n\n")
    
    # Process paragraphs
    for p in main_content.find_all('p'):
        p_text = p.get_text().strip()
        if p_text:
            content.append(f"{p_text}\n\n")
    
    # Process lists
    for ul in main_content.find_all('ul'):
        for li in ul.find_all('li'):
            li_text = li.get_text().strip()
            if li_text:
                content.append(f"- {li_text}\n")
        content.append("\n")
    
    for ol in main_content.find_all('ol'):
        for i, li in enumerate(ol.find_all('li'), 1):
            li_text = li.get_text().strip()
            if li_text:
                content.append(f"{i}. {li_text}\n")
        content.append("\n")
    
    # Process links
    for a in main_content.find_all('a'):
        href = a.get('href')
        text = a.get_text().strip()
        if href and text:
            # Resolve relative URLs if base_url is provided
            if base_url and href.startswith('/'):
                href = base_url.rstrip('/') + href
            
            # Replace the link with markdown format
            a_str = str(a)
            md_link = f"[{text}]({href})"
            for p in content:
                if a_str in p:
                    p = p.replace(a_str, md_link)
    
    # Process images
    for img in main_content.find_all('img'):
        src = img.get('src')
        alt = img.get('alt', '')
        if src:
            # Resolve relative URLs if base_url is provided
            if base_url and src.startswith('/'):
                src = base_url.rstrip('/') + src
            
            content.append(f"![{alt}]({src})\n\n")
    
    # Join all content
    return ''.join(content)

def html_to_mdp(
    html_data: Union[str, Path, bytes, io.BytesIO], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    base_url: Optional[str] = None
) -> Document:
    """
    Convert HTML data to an MDP document.
    
    Args:
        html_data: HTML data as a string, file path, bytes, or BytesIO object
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the HTML
        base_url: Optional base URL for resolving relative links
        
    Returns:
        An MDP Document object
        
    Raises:
        ImportError: If HTML support is not available
        ValueError: If html_data is invalid
    """
    _check_html_support()
    
    # Load the HTML data
    if isinstance(html_data, (str, Path)) and not html_data.startswith(('<', '<!DOCTYPE')):
        path = Path(html_data)
        if path.exists() and path.is_file():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except Exception as e:
                raise ValueError(f"Failed to read HTML file: {e}") from e
        else:
            # Assume it's an HTML string
            html_content = html_data
    elif isinstance(html_data, (bytes, io.BytesIO)):
        if isinstance(html_data, io.BytesIO):
            html_content = html_data.read().decode('utf-8')
        else:
            html_content = html_data.decode('utf-8')
    else:
        # Assume it's an HTML string
        html_content = html_data
    
    # Parse HTML
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        raise ValueError(f"Failed to parse HTML: {e}") from e
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata:
        doc_metadata = _extract_metadata_from_html(soup)
    
    # Override with provided metadata
    if metadata:
        # Normalize the provided metadata too
        normalized_metadata = normalize_metadata(metadata)
        doc_metadata.update(normalized_metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        # Try to use filename if available
        if isinstance(html_data, (str, Path)) and os.path.exists(html_data):
            filename = os.path.basename(html_data)
            base_name = os.path.splitext(filename)[0]
            doc_metadata["title"] = base_name.replace('_', ' ').replace('-', ' ').title()
        else:
            doc_metadata["title"] = "Converted HTML Document"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "html",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.html_converter"
    }
    
    # If base_url was provided, add it to source info
    if base_url:
        doc_metadata["source"]["base_url"] = base_url
    
    # Convert HTML to markdown
    content = _html_to_markdown(soup, base_url)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 