"""
Markdown to MDP converter.

This module provides functions to convert Markdown data to MDP format,
preserving structure and metadata.
"""

import os
import re
import frontmatter
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import datetime

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date

def _extract_title_from_markdown(content: str) -> Optional[str]:
    """
    Extract title from markdown content.
    
    Looks for the first heading (# Title) in the content.
    
    Args:
        content: The markdown content
        
    Returns:
        The extracted title or None if not found
    """
    # Look for a level 1 heading (# Title)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return None

def _extract_metadata_from_markdown(content: str, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from markdown content and frontmatter.
    
    Args:
        content: The markdown content
        frontmatter_data: The frontmatter data
        
    Returns:
        A dictionary of metadata
    """
    metadata = {}
    
    # First, extract from frontmatter if available
    if frontmatter_data:
        # Map frontmatter fields to MDP metadata fields
        metadata_fields = {
            "title": ["title", "name", "heading"],
            "description": ["description", "desc", "summary", "abstract"],
            "author": ["author", "creator", "owner", "authors"],
            "created_at": ["created_at", "created", "date", "created_date"],
            "updated_at": ["updated_at", "updated", "last_modified", "modified"],
            "version": ["version", "ver"],
            "tags": ["tags", "categories", "keywords"]
        }
        
        for meta_key, possible_keys in metadata_fields.items():
            for key in possible_keys:
                if key in frontmatter_data:
                    metadata[meta_key] = frontmatter_data[key]
                    break
    
    # If no title in frontmatter, try to extract from content
    if "title" not in metadata:
        title = _extract_title_from_markdown(content)
        if title:
            metadata["title"] = title
    
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

def _extract_tags_from_content(content: str) -> List[str]:
    """
    Extract potential tags from markdown content.
    
    Looks for hashtags and common tag patterns.
    
    Args:
        content: The markdown content
        
    Returns:
        A list of potential tags
    """
    tags = []
    
    # Look for hashtags (#tag) not at the beginning of a line (to avoid headings)
    hashtags = re.findall(r'(?<!\n)#([a-zA-Z0-9_-]+)', content)
    if hashtags:
        tags.extend(hashtags)
    
    # Look for "Tags: tag1, tag2" pattern
    tag_line_match = re.search(r'tags:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if tag_line_match:
        tag_line = tag_line_match.group(1)
        line_tags = [t.strip() for t in tag_line.split(',')]
        tags.extend(line_tags)
    
    # Remove duplicates and return
    return list(set(tags))

def markdown_to_mdp(
    markdown_data: Union[str, Path], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    preserve_frontmatter: bool = False
) -> Document:
    """
    Convert Markdown data to an MDP document.
    
    Args:
        markdown_data: Markdown data as a string or file path
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the Markdown
        preserve_frontmatter: Whether to preserve frontmatter in the content
        
    Returns:
        An MDP Document object
        
    Raises:
        ValueError: If markdown_data is invalid
    """
    # Load the Markdown data
    if isinstance(markdown_data, Path) or (isinstance(markdown_data, str) and os.path.exists(markdown_data)):
        try:
            with open(markdown_data, 'r', encoding='utf-8') as f:
                raw_content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read Markdown file: {e}") from e
    else:
        # It's a string
        raw_content = markdown_data
    
    # Parse frontmatter if present
    try:
        parsed = frontmatter.loads(raw_content)
        frontmatter_data = parsed.metadata
        content = parsed.content
    except Exception:
        # If frontmatter parsing fails, assume no frontmatter
        frontmatter_data = {}
        content = raw_content
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata:
        doc_metadata = _extract_metadata_from_markdown(content, frontmatter_data)
        
        # If no tags found in frontmatter, try to extract from content
        if "tags" not in doc_metadata:
            tags = _extract_tags_from_content(content)
            if tags:
                doc_metadata["tags"] = tags
    
    # Override with provided metadata
    if metadata:
        doc_metadata.update(metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        # Try to use filename if available
        if isinstance(markdown_data, (str, Path)) and os.path.exists(markdown_data):
            filename = os.path.basename(markdown_data)
            base_name = os.path.splitext(filename)[0]
            doc_metadata["title"] = base_name.replace('_', ' ').replace('-', ' ').title()
        else:
            doc_metadata["title"] = "Converted Markdown Document"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "markdown",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.markdown_converter"
    }
    
    # Determine final content
    if preserve_frontmatter and frontmatter_data:
        # Reconstruct the original content with frontmatter
        final_content = frontmatter.dumps(frontmatter.Post(content, **frontmatter_data))
    else:
        # Just use the content without frontmatter
        final_content = content
    
    # Create the document
    doc = Document.create(
        content=final_content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 