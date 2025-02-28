"""
API Response to MDP converter.

This module provides functions to convert API responses (JSON/XML) to MDP format,
preserving structure and metadata.
"""

import os
import io
import json
import datetime
import re
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date
from .utils import normalize_metadata

def _extract_metadata_from_api_response(
    response_data: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    url: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    response_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    Extract metadata from an API response.
    
    Args:
        response_data: The API response data
        headers: Optional response headers
        url: Optional request URL
        method: Optional request method
        status_code: Optional response status code
        response_time: Optional response time in seconds
        
    Returns:
        A dictionary of metadata
    """
    metadata = {}
    
    # Try to extract a title from common fields
    title_fields = ['title', 'name', 'label', 'id', 'type']
    for field in title_fields:
        if field in response_data:
            metadata['title'] = f"API Response: {response_data[field]}"
            break
    
    # Add API request/response information
    api_info = {}
    
    if url:
        api_info['url'] = url
    
    if method:
        api_info['method'] = method
    
    if status_code:
        api_info['status_code'] = status_code
    
    if response_time:
        api_info['response_time'] = f"{response_time:.3f} seconds"
    
    if headers:
        # Extract useful headers
        useful_headers = [
            'content-type', 'date', 'server', 'x-rate-limit', 
            'x-rate-limit-remaining', 'x-rate-limit-reset',
            'cache-control', 'expires', 'last-modified'
        ]
        
        extracted_headers = {}
        for header, value in headers.items():
            header_lower = header.lower()
            if header_lower in useful_headers or header_lower.startswith('x-'):
                extracted_headers[header] = value
        
        if extracted_headers:
            api_info['headers'] = extracted_headers
    
    if api_info:
        metadata['api_info'] = api_info
    
    # Try to extract date information
    date_fields = ['date', 'created', 'created_at', 'timestamp', 'time']
    for field in date_fields:
        if field in response_data:
            try:
                metadata['created_at'] = format_date(response_data[field])
                break
            except (ValueError, TypeError):
                # If parsing fails, continue to the next field
                continue
    
    # Extract other potentially useful fields
    for field in response_data:
        if field not in title_fields + date_fields and not field.startswith('_'):
            # Skip complex nested objects
            if not isinstance(response_data[field], (dict, list)):
                metadata[field] = response_data[field]
    
    # Normalize metadata to conform to MDP standards
    return normalize_metadata(metadata)

def _format_json_value(value: Any, indent: int = 0) -> str:
    """
    Format a JSON value for markdown display.
    
    Args:
        value: The value to format
        indent: The current indentation level
        
    Returns:
        Formatted string representation of the value
    """
    if value is None:
        return "*null*"
    elif isinstance(value, bool):
        return "`true`" if value else "`false`"
    elif isinstance(value, (int, float)):
        return f"`{value}`"
    elif isinstance(value, str):
        if len(value) > 100:
            return f'"{value[:100]}..."'
        else:
            return f'"{value}"'
    elif isinstance(value, list):
        if not value:
            return "[ ]"
        elif len(value) > 5:
            return f"[ *{len(value)} items* ]"
        else:
            items = [_format_json_value(item, indent + 2) for item in value]
            return "[ " + ", ".join(items) + " ]"
    elif isinstance(value, dict):
        if not value:
            return "{ }"
        elif len(value) > 5:
            return f"{{ *{len(value)} properties* }}"
        else:
            return "{ ... }"
    else:
        return str(value)

def _json_to_markdown_table(data: Dict[str, Any], max_depth: int = 2, current_depth: int = 0) -> str:
    """
    Convert a JSON object to a markdown table.
    
    Args:
        data: The JSON object to convert
        max_depth: Maximum depth to render in detail
        current_depth: Current depth in the JSON structure
        
    Returns:
        Markdown table representation of the JSON object
    """
    if current_depth >= max_depth:
        return "*Nested data (depth > {max_depth})*"
    
    if not isinstance(data, dict):
        return str(data)
    
    # Create table
    table = []
    
    # Add header row
    table.append("| Property | Value |")
    table.append("| --- | --- |")
    
    # Add data rows
    for key, value in data.items():
        if isinstance(value, dict) and current_depth < max_depth - 1:
            # Recursively format nested objects
            nested_table = _json_to_markdown_table(value, max_depth, current_depth + 1)
            table.append(f"| **{key}** | *Object:* |\n\n{nested_table}\n")
        elif isinstance(value, list) and current_depth < max_depth - 1:
            # Format list items
            if not value:
                table.append(f"| **{key}** | *Empty array* |")
            elif all(isinstance(item, dict) for item in value):
                # List of objects - show count and first item
                table.append(f"| **{key}** | *Array of {len(value)} objects* |")
                if value:
                    nested_table = _json_to_markdown_table(value[0], max_depth, current_depth + 1)
                    table.append(f"\n*First item:*\n\n{nested_table}\n")
            else:
                # Simple list - show formatted values
                formatted_items = [_format_json_value(item, current_depth) for item in value[:5]]
                if len(value) > 5:
                    formatted_items.append("...")
                table.append(f"| **{key}** | {', '.join(formatted_items)} |")
        else:
            # Format simple values
            formatted_value = _format_json_value(value, current_depth)
            table.append(f"| **{key}** | {formatted_value} |")
    
    return "\n".join(table)

def _api_response_to_markdown(
    response_data: Union[Dict[str, Any], str],
    format_type: str = 'json',
    url: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    headers: Optional[Dict[str, str]] = None,
    response_time: Optional[float] = None,
    max_depth: int = 3
) -> str:
    """
    Convert an API response to markdown.
    
    Args:
        response_data: The API response data
        format_type: The format of the response ('json' or 'xml')
        url: Optional request URL
        method: Optional request method
        status_code: Optional response status code
        headers: Optional response headers
        response_time: Optional response time in seconds
        max_depth: Maximum depth to render in detail
        
    Returns:
        Markdown representation of the API response
    """
    content = []
    
    # Add API request information
    if url or method or status_code:
        content.append("## API Request\n")
        
        if method and url:
            content.append(f"**{method}** {url}\n")
        elif url:
            content.append(f"**URL:** {url}\n")
        elif method:
            content.append(f"**Method:** {method}\n")
        
        if status_code:
            status_text = "Success" if 200 <= status_code < 300 else "Error"
            content.append(f"**Status:** {status_code} ({status_text})\n")
        
        if response_time:
            content.append(f"**Response Time:** {response_time:.3f} seconds\n")
        
        content.append("")
    
    # Add headers if provided
    if headers:
        content.append("## Response Headers\n")
        
        # Create a table for headers
        content.append("| Header | Value |")
        content.append("| --- | --- |")
        
        for header, value in headers.items():
            content.append(f"| {header} | {value} |")
        
        content.append("")
    
    # Add response body
    content.append("## Response Body\n")
    
    if format_type.lower() == 'json':
        # Ensure we have a dictionary
        if isinstance(response_data, str):
            try:
                response_dict = json.loads(response_data)
            except json.JSONDecodeError:
                # If it's not valid JSON, just show as text
                content.append("```\n" + response_data + "\n```")
                return "\n".join(content)
        else:
            response_dict = response_data
        
        # Add raw JSON
        content.append("### Raw JSON\n")
        content.append("```json")
        content.append(json.dumps(response_dict, indent=2))
        content.append("```\n")
        
        # Add structured view
        content.append("### Structured View\n")
        content.append(_json_to_markdown_table(response_dict, max_depth))
    
    elif format_type.lower() == 'xml':
        # Ensure we have a string
        if not isinstance(response_data, str):
            response_str = str(response_data)
        else:
            response_str = response_data
        
        # Add raw XML
        content.append("### Raw XML\n")
        content.append("```xml")
        content.append(response_str)
        content.append("```\n")
        
        # Try to parse XML and show structure
        try:
            root = ET.fromstring(response_str)
            
            content.append("### XML Structure\n")
            
            # Create a simple representation of the XML structure
            def format_element(element, indent=0):
                result = []
                indent_str = "  " * indent
                
                # Add element with attributes
                attrs = ""
                if element.attrib:
                    attrs = " " + " ".join([f'{k}="{v}"' for k, v in element.attrib.items()])
                
                if len(element) == 0 and not element.text:
                    result.append(f"{indent_str}- <{element.tag}{attrs} />")
                else:
                    result.append(f"{indent_str}- <{element.tag}{attrs}>")
                    
                    # Add text content if present
                    if element.text and element.text.strip():
                        text = element.text.strip()
                        if len(text) > 50:
                            text = text[:50] + "..."
                        result.append(f"{indent_str}  Text: \"{text}\"")
                    
                    # Add children recursively
                    for child in element:
                        result.extend(format_element(child, indent + 1))
                
                return result
            
            structure = format_element(root)
            content.append("\n".join(structure))
        
        except ET.ParseError:
            content.append("*Could not parse XML structure*")
    
    else:
        # Unknown format, just show as text
        content.append("```")
        content.append(str(response_data))
        content.append("```")
    
    return "\n".join(content)

def api_response_to_mdp(
    response_data: Union[Dict[str, Any], str, bytes, io.BytesIO],
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    format_type: str = 'json',
    url: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    headers: Optional[Dict[str, str]] = None,
    response_time: Optional[float] = None,
    max_depth: int = 3
) -> Document:
    """
    Convert an API response to an MDP document.
    
    Args:
        response_data: The API response data
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        format_type: The format of the response ('json' or 'xml')
        url: Optional request URL
        method: Optional request method
        status_code: Optional response status code
        headers: Optional response headers
        response_time: Optional response time in seconds
        max_depth: Maximum depth to render in detail
        
    Returns:
        An MDP Document object
        
    Raises:
        ValueError: If response_data is invalid
    """
    # Load the response data
    if isinstance(response_data, (bytes, io.BytesIO)):
        try:
            if isinstance(response_data, io.BytesIO):
                response_str = response_data.read().decode('utf-8')
            else:
                response_str = response_data.decode('utf-8')
            
            # Try to parse as JSON
            if format_type.lower() == 'json':
                try:
                    response_obj = json.loads(response_str)
                except json.JSONDecodeError:
                    # If it's not valid JSON, keep as string
                    response_obj = response_str
            else:
                # For XML or other formats, keep as string
                response_obj = response_str
        except UnicodeDecodeError:
            raise ValueError("Failed to decode response data as UTF-8")
    elif isinstance(response_data, str):
        # Try to parse as JSON if format is JSON
        if format_type.lower() == 'json':
            try:
                response_obj = json.loads(response_data)
            except json.JSONDecodeError:
                # If it's not valid JSON, keep as string
                response_obj = response_data
        else:
            # For XML or other formats, keep as string
            response_obj = response_data
    elif isinstance(response_data, (dict, list)):
        # Already a Python object
        response_obj = response_data
    else:
        raise ValueError("Invalid response data type. Expected dict, list, string, bytes, or BytesIO object.")
    
    # Extract metadata if possible
    doc_metadata = {}
    if isinstance(response_obj, dict):
        doc_metadata = _extract_metadata_from_api_response(
            response_obj,
            headers=headers,
            url=url,
            method=method,
            status_code=status_code,
            response_time=response_time
        )
    
    # Override with provided metadata
    if metadata:
        # Normalize the provided metadata too
        normalized_metadata = normalize_metadata(metadata)
        doc_metadata.update(normalized_metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        # Create a title based on available information
        title_parts = []
        
        if method:
            title_parts.append(method)
        
        if url:
            # Extract endpoint from URL
            url_path = url.split('://')[-1].split('/', 1)[-1] if '://' in url else url
            endpoint = url_path.split('?')[0]  # Remove query parameters
            if endpoint:
                title_parts.append(endpoint)
        
        if status_code:
            title_parts.append(f"Status {status_code}")
        
        if title_parts:
            doc_metadata["title"] = "API Response: " + " - ".join(title_parts)
        else:
            doc_metadata["title"] = f"API Response ({format_type.upper()})"
    
    # Add source information
    doc_metadata["source"] = {
        "type": f"api_{format_type.lower()}",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.api_converter"
    }
    
    # Add API info to source if available
    if "x_api_info" in doc_metadata:
        doc_metadata["source"].update(doc_metadata.pop("x_api_info"))
    
    # Convert response to markdown
    content = _api_response_to_markdown(
        response_obj,
        format_type=format_type,
        url=url,
        method=method,
        status_code=status_code,
        headers=headers,
        response_time=response_time,
        max_depth=max_depth
    )
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 