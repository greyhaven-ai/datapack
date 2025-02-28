"""
JSON to MDP converter.

This module provides functions to convert JSON data to MDP format,
preserving structure and metadata.
"""

import json
import os
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import datetime

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid

def _flatten_json(
    json_obj: Any, 
    parent_key: str = '', 
    separator: str = '.', 
    max_depth: int = 3,
    current_depth: int = 0
) -> Dict[str, Any]:
    """
    Flatten a nested JSON object to a flat dictionary with dot notation keys.
    
    Args:
        json_obj: The JSON object to flatten
        parent_key: The parent key for nested objects
        separator: The separator to use between keys
        max_depth: Maximum depth to flatten
        current_depth: Current depth in recursion
        
    Returns:
        A flattened dictionary
    """
    items = {}
    
    # If we've reached max depth, just store the value as is
    if current_depth >= max_depth and isinstance(json_obj, (dict, list)):
        return {parent_key: json_obj}
    
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            new_key = f"{parent_key}{separator}{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                items.update(_flatten_json(v, new_key, separator, max_depth, current_depth + 1))
            else:
                items[new_key] = v
    elif isinstance(json_obj, list):
        for i, v in enumerate(json_obj):
            new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
            if isinstance(v, (dict, list)):
                items.update(_flatten_json(v, new_key, separator, max_depth, current_depth + 1))
            else:
                items[new_key] = v
    else:
        items[parent_key] = json_obj
        
    return items

def _extract_metadata_from_json(json_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a JSON object.
    
    Args:
        json_obj: The JSON object to extract metadata from
        
    Returns:
        A dictionary of metadata
    """
    metadata = {}
    
    # Try to extract common metadata fields
    if isinstance(json_obj, dict):
        # Look for common metadata fields
        metadata_fields = {
            "title": ["title", "name", "heading"],
            "description": ["description", "desc", "summary"],
            "author": ["author", "creator", "owner"],
            "created_at": ["created_at", "created", "createdAt", "creation_date", "date"],
            "updated_at": ["updated_at", "updated", "updatedAt", "last_modified"],
            "version": ["version", "v", "ver"],
            "tags": ["tags", "categories", "keywords"]
        }
        
        for meta_key, possible_keys in metadata_fields.items():
            for key in possible_keys:
                if key in json_obj:
                    metadata[meta_key] = json_obj[key]
                    break
    
    # Ensure we have a title
    if "title" not in metadata and isinstance(json_obj, dict):
        # Try to use a field that might work as a title
        for key in ["id", "name", "key"]:
            if key in json_obj:
                metadata["title"] = f"JSON: {json_obj[key]}"
                break
        else:
            metadata["title"] = "Converted JSON Document"
    
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

def json_to_markdown(json_obj: Any, indent: int = 0, max_depth: int = 5) -> str:
    """
    Convert a JSON object to a markdown representation.
    
    Args:
        json_obj: The JSON object to convert
        indent: The current indentation level
        max_depth: Maximum depth to render in detail
        
    Returns:
        A markdown string representation of the JSON
    """
    if indent > max_depth:
        return f"*Nested data (depth > {max_depth})*\n"
    
    result = []
    
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            prefix = "#" * (indent + 2) if indent < 4 else "##" + "#" * (indent - 3)
            
            if isinstance(value, (dict, list)):
                result.append(f"{prefix} {key}\n")
                result.append(json_to_markdown(value, indent + 1, max_depth))
            else:
                # Format the value based on its type
                formatted_value = value
                if value is None:
                    formatted_value = "*null*"
                elif isinstance(value, bool):
                    formatted_value = "`true`" if value else "`false`"
                elif isinstance(value, (int, float)):
                    formatted_value = f"`{value}`"
                
                result.append(f"{prefix} {key}: {formatted_value}\n")
    
    elif isinstance(json_obj, list):
        for item in json_obj:
            if isinstance(item, (dict, list)):
                result.append(json_to_markdown(item, indent, max_depth))
            else:
                result.append(f"- {item}\n")
    
    else:
        result.append(str(json_obj))
    
    return "".join(result)

def json_to_mdp(
    json_data: Union[str, Dict[str, Any], Path], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    max_depth: int = 5
) -> Document:
    """
    Convert JSON data to an MDP document.
    
    Args:
        json_data: JSON data as a string, dictionary, or file path
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the JSON
        max_depth: Maximum depth to render in detail
        
    Returns:
        An MDP Document object
        
    Raises:
        ValueError: If json_data is invalid
    """
    # Load the JSON data
    if isinstance(json_data, (str, Path)) and not isinstance(json_data, dict):
        path = Path(json_data)
        if path.exists() and path.is_file():
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    json_obj = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON file: {e}") from e
        else:
            # Try parsing as a JSON string
            try:
                json_obj = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON data: {e}") from e
    elif isinstance(json_data, dict):
        json_obj = json_data
    else:
        raise ValueError("json_data must be a JSON string, dictionary, or file path")
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata:
        doc_metadata = _extract_metadata_from_json(json_obj)
    
    # Override with provided metadata
    if metadata:
        doc_metadata.update(metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        doc_metadata["title"] = "Converted JSON Document"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "json",
        "converted_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "converter": "datapack.converters.json_converter"
    }
    
    # Create markdown content from JSON
    content = f"# {doc_metadata.get('title')}\n\n"
    if "description" in doc_metadata:
        content += f"{doc_metadata['description']}\n\n"
    
    content += "## JSON Data\n\n"
    content += json_to_markdown(json_obj, indent=1, max_depth=max_depth)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 