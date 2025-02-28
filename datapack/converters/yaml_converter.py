"""
YAML to MDP converter.

This module provides functions to convert YAML data to MDP format,
preserving structure and metadata.
"""

import os
import yaml
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import datetime

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date

def _extract_metadata_from_yaml(yaml_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a YAML object.
    
    Args:
        yaml_obj: The YAML object to extract metadata from
        
    Returns:
        A dictionary of metadata
    """
    metadata = {}
    
    # Try to extract common metadata fields
    if isinstance(yaml_obj, dict):
        # Look for common metadata fields
        metadata_fields = {
            "title": ["title", "name", "heading", "document_title"],
            "description": ["description", "desc", "summary", "abstract"],
            "author": ["author", "creator", "owner", "created_by", "maintainer"],
            "created_at": ["created_at", "created", "creation_date", "date_created", "date"],
            "updated_at": ["updated_at", "updated", "last_modified", "modified", "modification_date"],
            "version": ["version", "ver", "document_version"],
            "tags": ["tags", "categories", "keywords", "labels"]
        }
        
        for meta_key, possible_keys in metadata_fields.items():
            for key in possible_keys:
                if key in yaml_obj:
                    metadata[meta_key] = yaml_obj[key]
                    break
    
    # Ensure we have a title
    if "title" not in metadata and isinstance(yaml_obj, dict):
        # Try to use a field that might work as a title
        for key in ["id", "name", "key", "document"]:
            if key in yaml_obj:
                metadata["title"] = f"YAML: {yaml_obj[key]}"
                break
        else:
            metadata["title"] = "Converted YAML Document"
    
    # Format dates if needed
    for date_field in ["created_at", "updated_at"]:
        if date_field in metadata and isinstance(metadata[date_field], str):
            try:
                # Use the mdp format_date utility
                metadata[date_field] = format_date(metadata[date_field])
            except (ValueError, TypeError):
                # If parsing fails, keep as is
                pass
    
    return metadata

def yaml_to_markdown(yaml_obj: Any, indent: int = 0, max_depth: int = 5) -> str:
    """
    Convert a YAML object to a markdown representation.
    
    Args:
        yaml_obj: The YAML object to convert
        indent: The current indentation level
        max_depth: Maximum depth to render in detail
        
    Returns:
        A markdown string representation of the YAML
    """
    if indent > max_depth:
        return f"*Nested data (depth > {max_depth})*\n"
    
    result = []
    
    if isinstance(yaml_obj, dict):
        for key, value in yaml_obj.items():
            prefix = "#" * (indent + 2) if indent < 4 else "##" + "#" * (indent - 3)
            
            if isinstance(value, (dict, list)):
                result.append(f"{prefix} {key}\n")
                result.append(yaml_to_markdown(value, indent + 1, max_depth))
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
    
    elif isinstance(yaml_obj, list):
        for item in yaml_obj:
            if isinstance(item, (dict, list)):
                result.append(yaml_to_markdown(item, indent, max_depth))
            else:
                result.append(f"- {item}\n")
    
    else:
        result.append(str(yaml_obj))
    
    return "".join(result)

def yaml_to_mdp(
    yaml_data: Union[str, Dict[str, Any], Path], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    max_depth: int = 5
) -> Document:
    """
    Convert YAML data to an MDP document.
    
    Args:
        yaml_data: YAML data as a string, dictionary, or file path
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the YAML
        max_depth: Maximum depth to render in detail
        
    Returns:
        An MDP Document object
        
    Raises:
        ValueError: If yaml_data is invalid
    """
    # Load the YAML data
    if isinstance(yaml_data, (str, Path)) and not isinstance(yaml_data, dict):
        path = Path(yaml_data)
        if path.exists() and path.is_file():
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    yaml_obj = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid YAML file: {e}") from e
        else:
            # Try parsing as a YAML string
            try:
                yaml_obj = yaml.safe_load(yaml_data)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML data: {e}") from e
    elif isinstance(yaml_data, dict):
        yaml_obj = yaml_data
    else:
        raise ValueError("yaml_data must be a YAML string, dictionary, or file path")
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata and isinstance(yaml_obj, dict):
        doc_metadata = _extract_metadata_from_yaml(yaml_obj)
    
    # Override with provided metadata
    if metadata:
        doc_metadata.update(metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        doc_metadata["title"] = "Converted YAML Document"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "yaml",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.yaml_converter"
    }
    
    # Create markdown content from YAML
    content = f"# {doc_metadata.get('title')}\n\n"
    if "description" in doc_metadata:
        content += f"{doc_metadata['description']}\n\n"
    
    content += "## YAML Data\n\n"
    content += yaml_to_markdown(yaml_obj, indent=1, max_depth=max_depth)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 