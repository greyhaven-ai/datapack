"""
Jupyter Notebook to MDP converter.

This module provides functions to convert Jupyter Notebook files to MDP format,
preserving code, markdown, and outputs.
"""

import os
import io
import json
import datetime
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path

try:
    import nbformat
    from nbconvert import MarkdownExporter
    NOTEBOOK_SUPPORT = True
except ImportError:
    NOTEBOOK_SUPPORT = False

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date
from .utils import normalize_metadata

def _check_notebook_support():
    """
    Check if Jupyter Notebook support is available.
    
    Raises:
        ImportError: If Jupyter Notebook support is not available
    """
    if not NOTEBOOK_SUPPORT:
        raise ImportError(
            "Jupyter Notebook support requires additional dependencies. "
            "Install with 'pip install datapack[converters]' or 'pip install nbformat nbconvert'"
        )

def _extract_metadata_from_notebook(notebook: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a Jupyter Notebook.
    
    Args:
        notebook: A Jupyter Notebook object
        
    Returns:
        A dictionary of metadata
    """
    _check_notebook_support()
    
    metadata = {}
    
    # Extract notebook metadata
    nb_metadata = notebook.get('metadata', {})
    
    # Try to extract title from the first markdown cell with a heading
    cells = notebook.get('cells', [])
    for cell in cells:
        if cell.get('cell_type') == 'markdown':
            source = cell.get('source', '')
            if isinstance(source, list):
                source = ''.join(source)
            
            # Look for a heading
            import re
            heading_match = re.search(r'^#\s+(.+)$', source, re.MULTILINE)
            if heading_match:
                metadata['title'] = heading_match.group(1).strip()
                break
    
    # Extract kernel info (as custom field, will be normalized later)
    if 'kernelspec' in nb_metadata:
        kernel_info = nb_metadata['kernelspec']
        metadata['kernel'] = {
            'name': kernel_info.get('name', ''),
            'display_name': kernel_info.get('display_name', '')
        }
    
    # Extract language info (as custom field, will be normalized later)
    if 'language_info' in nb_metadata:
        lang_info = nb_metadata['language_info']
        metadata['language'] = {
            'name': lang_info.get('name', ''),
            'version': lang_info.get('version', '')
        }
    
    # Extract author info if available
    if 'author' in nb_metadata:
        metadata['author'] = nb_metadata['author']
    
    # Extract tags
    tags = []
    for cell in cells:
        cell_metadata = cell.get('metadata', {})
        cell_tags = cell_metadata.get('tags', [])
        if cell_tags:
            tags.extend(cell_tags)
    
    if tags:
        metadata['tags'] = list(set(tags))  # Remove duplicates
    
    # Add other notebook metadata as custom fields
    for key, value in nb_metadata.items():
        if key not in ['kernelspec', 'language_info', 'author'] and not isinstance(value, dict):
            metadata[key] = value
    
    # Normalize metadata to conform to MDP standards
    return normalize_metadata(metadata)

def _notebook_to_markdown(notebook: Dict[str, Any], include_outputs: bool = True) -> str:
    """
    Convert a Jupyter Notebook to markdown.
    
    Args:
        notebook: A Jupyter Notebook object
        include_outputs: Whether to include cell outputs
        
    Returns:
        Markdown representation of the notebook
    """
    _check_notebook_support()
    
    # Convert notebook to nbformat.NotebookNode if it's a dict
    if isinstance(notebook, dict):
        notebook = nbformat.from_dict(notebook)
    
    # Use nbconvert to convert to markdown
    exporter = MarkdownExporter()
    
    # Configure exporter
    if not include_outputs:
        exporter.exclude_output = True
    
    # Convert to markdown
    markdown, _ = exporter.from_notebook_node(notebook)
    
    return markdown

def notebook_to_mdp(
    notebook_data: Union[str, Path, Dict[str, Any], bytes, io.BytesIO], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    include_outputs: bool = True
) -> Document:
    """
    Convert Jupyter Notebook data to an MDP document.
    
    Args:
        notebook_data: Notebook data as a file path, dict, bytes, or BytesIO object
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the notebook
        include_outputs: Whether to include cell outputs in the markdown
        
    Returns:
        An MDP Document object
        
    Raises:
        ImportError: If Jupyter Notebook support is not available
        ValueError: If notebook_data is invalid
    """
    _check_notebook_support()
    
    # Load the notebook data
    try:
        if isinstance(notebook_data, (str, Path)):
            # Load from file
            notebook = nbformat.read(notebook_data, as_version=4)
            # Use filename as title if available
            filename = os.path.basename(notebook_data)
            base_name = os.path.splitext(filename)[0]
            default_title = base_name.replace('_', ' ').replace('-', ' ').title()
        elif isinstance(notebook_data, dict):
            # Already a notebook dict
            notebook = nbformat.from_dict(notebook_data)
            default_title = "Converted Jupyter Notebook"
        elif isinstance(notebook_data, bytes):
            # Load from bytes
            notebook_str = notebook_data.decode('utf-8')
            notebook_dict = json.loads(notebook_str)
            notebook = nbformat.from_dict(notebook_dict)
            default_title = "Converted Jupyter Notebook"
        elif isinstance(notebook_data, io.BytesIO):
            # Load from BytesIO
            notebook_str = notebook_data.read().decode('utf-8')
            notebook_dict = json.loads(notebook_str)
            notebook = nbformat.from_dict(notebook_dict)
            default_title = "Converted Jupyter Notebook"
        else:
            raise ValueError("Invalid notebook data type. Expected file path, dict, bytes, or BytesIO object.")
    except Exception as e:
        raise ValueError(f"Failed to read Jupyter Notebook: {e}") from e
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata:
        doc_metadata = _extract_metadata_from_notebook(notebook)
    
    # Override with provided metadata
    if metadata:
        # Normalize the provided metadata too
        normalized_metadata = normalize_metadata(metadata)
        doc_metadata.update(normalized_metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        doc_metadata["title"] = default_title
    
    # Add source information
    doc_metadata["source"] = {
        "type": "jupyter_notebook",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.notebook_converter"
    }
    
    # Add kernel and language info to source if available
    if 'x_kernel' in doc_metadata:
        doc_metadata["source"]["kernel"] = doc_metadata.pop("x_kernel")
    if 'x_language' in doc_metadata:
        doc_metadata["source"]["language"] = doc_metadata.pop("x_language")
    
    # Convert notebook to markdown
    content = _notebook_to_markdown(notebook, include_outputs)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 