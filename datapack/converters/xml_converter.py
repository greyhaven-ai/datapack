"""
XML to MDP converter.

This module provides functions to convert XML data to MDP format,
preserving structure and metadata.
"""

import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import datetime

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid

def _extract_metadata_from_xml(root: ET.Element) -> Dict[str, Any]:
    """
    Extract metadata from an XML root element.
    
    Args:
        root: The XML root element
        
    Returns:
        A dictionary of metadata
    """
    metadata = {}
    
    # Look for common metadata fields in attributes
    metadata_fields = {
        "title": ["title", "name", "heading"],
        "description": ["description", "desc", "summary"],
        "author": ["author", "creator", "owner"],
        "created_at": ["created_at", "created", "createdAt", "creation_date", "date"],
        "updated_at": ["updated_at", "updated", "updatedAt", "last_modified"],
        "version": ["version", "v", "ver"],
    }
    
    # Check root attributes first
    for meta_key, possible_keys in metadata_fields.items():
        for key in possible_keys:
            if key in root.attrib:
                metadata[meta_key] = root.attrib[key]
                break
    
    # Look for metadata in child elements
    for meta_key, possible_keys in metadata_fields.items():
        if meta_key in metadata:
            continue  # Already found in attributes
            
        for key in possible_keys:
            elements = root.findall(f".//{key}")
            if elements and len(elements) > 0 and elements[0].text:
                metadata[meta_key] = elements[0].text
                break
    
    # If no title found, use the root tag
    if "title" not in metadata:
        metadata["title"] = f"XML: {root.tag}"
    
    # Look for tags/categories
    tags = []
    for tag_element in root.findall(".//tag") + root.findall(".//category") + root.findall(".//keyword"):
        if tag_element.text:
            tags.append(tag_element.text)
    
    if tags:
        metadata["tags"] = tags
    
    # Format dates if needed
    for date_field in ["created_at", "updated_at"]:
        if date_field in metadata and isinstance(metadata[date_field], str):
            try:
                # Simple attempt to parse ISO format
                date_obj = datetime.datetime.fromisoformat(metadata[date_field].replace('Z', '+00:00'))
                metadata[date_field] = date_obj.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                # If parsing fails, keep as is
                pass
    
    return metadata

def _element_to_markdown(
    element: ET.Element, 
    indent: int = 0, 
    max_depth: int = 5,
    include_attributes: bool = True
) -> str:
    """
    Convert an XML element to markdown.
    
    Args:
        element: The XML element to convert
        indent: The current indentation level
        max_depth: Maximum depth to render in detail
        include_attributes: Whether to include attributes
        
    Returns:
        A markdown string representation of the XML element
    """
    if indent > max_depth:
        return f"*Nested XML (depth > {max_depth})*\n"
    
    result = []
    
    # Create heading based on indent level
    prefix = "#" * (indent + 2) if indent < 4 else "##" + "#" * (indent - 3)
    
    # Element name as heading
    result.append(f"{prefix} {element.tag}\n")
    
    # Add attributes if available and requested
    if include_attributes and element.attrib:
        result.append("**Attributes:**\n\n")
        for attr_name, attr_value in element.attrib.items():
            result.append(f"- *{attr_name}*: `{attr_value}`\n")
        result.append("\n")
    
    # Add text content if available
    if element.text and element.text.strip():
        text = element.text.strip()
        # For short text, display inline
        if len(text) < 100:
            result.append(f"{text}\n\n")
        else:
            # For longer text, use blockquote
            result.append("> " + text.replace("\n", "\n> ") + "\n\n")
    
    # Process child elements
    for child in element:
        result.append(_element_to_markdown(child, indent + 1, max_depth, include_attributes))
    
    return "".join(result)

def xml_to_mdp(
    xml_data: Union[str, Path], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    max_depth: int = 5,
    include_attributes: bool = True
) -> Document:
    """
    Convert XML data to an MDP document.
    
    Args:
        xml_data: XML data as a string or file path
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the XML
        max_depth: Maximum depth to render in detail
        include_attributes: Whether to include XML attributes in the output
        
    Returns:
        An MDP Document object
        
    Raises:
        ValueError: If xml_data is invalid
    """
    # Parse the XML data
    try:
        if isinstance(xml_data, (str, Path)) and os.path.exists(str(xml_data)):
            tree = ET.parse(str(xml_data))
            root = tree.getroot()
        else:
            root = ET.fromstring(xml_data)
    except Exception as e:
        raise ValueError(f"Invalid XML data: {e}") from e
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata:
        doc_metadata = _extract_metadata_from_xml(root)
    
    # Override with provided metadata
    if metadata:
        doc_metadata.update(metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        doc_metadata["title"] = "Converted XML Document"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "xml",
        "converted_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "converter": "datapack.converters.xml_converter"
    }
    
    # Create markdown content from XML
    content = f"# {doc_metadata.get('title')}\n\n"
    if "description" in doc_metadata:
        content += f"{doc_metadata['description']}\n\n"
    
    content += "## XML Structure\n\n"
    content += _element_to_markdown(root, indent=1, max_depth=max_depth, include_attributes=include_attributes)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 