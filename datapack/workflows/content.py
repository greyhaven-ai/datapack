"""
Content workflows for MDP documents.

This module provides functions for working with and manipulating
the content of MDP documents, such as batch processing and
content extraction.
"""

import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union, Tuple
import shutil

from mdp.document import Document
from mdp.collection import Collection
from mdp.utils import find_mdp_files, extract_metadata_from_content

# Attempt to import AI capabilities, but don't fail if not available
try:
    from datapack.ai.agents import (
        DocumentProcessingAgent, 
        ContentEnhancementAgent,
        configure_ai,
        ai_settings
    )
    from datapack.ai.models import AISettings
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


def batch_process_documents(
    source_directory: Union[str, Path],
    processor_function: Callable[[Document], Document],
    output_directory: Optional[Union[str, Path]] = None,
    include_pattern: str = "*.mdp",
    recursive: bool = True,
    dry_run: bool = False,
    backup: bool = True
) -> List[Document]:
    """
    Batch process a collection of MDP documents.
    
    This function applies a processor function to each document in a directory,
    optionally saving the results to a new location.
    
    Args:
        source_directory: Directory containing source MDP documents
        processor_function: Function to apply to each document
        output_directory: Directory to save processed documents (if None, overwrite source)
        include_pattern: Pattern to match MDP files
        recursive: Whether to search directories recursively
        dry_run: If True, don't actually write files
        backup: Whether to backup original files when overwriting
        
    Returns:
        List of processed Document objects
    """
    source_dir = Path(source_directory)
    
    # Determine output directory
    output_dir = None
    if output_directory:
        output_dir = Path(output_directory)
        os.makedirs(output_dir, exist_ok=True)
    
    # Find MDP files
    mdp_files = find_mdp_files(source_dir, include_pattern=include_pattern, recursive=recursive)
    
    # Process each file
    processed_docs = []
    for file_path in mdp_files:
        try:
            # Load the document
            doc = Document.from_file(file_path)
            
            # Process the document
            processed_doc = processor_function(doc)
            
            if not processed_doc:
                print(f"Warning: Processor returned None for {file_path}")
                continue
                
            # Determine output path
            if output_dir:
                rel_path = file_path.relative_to(source_dir)
                output_path = output_dir / rel_path
                # Ensure parent directory exists
                os.makedirs(output_path.parent, exist_ok=True)
                processed_doc._mdp_file.path = output_path
            else:
                # In-place update
                processed_doc._mdp_file.path = file_path
                
                # Create backup if requested
                if backup and not dry_run:
                    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                    shutil.copy2(file_path, backup_path)
            
            # Save the document unless this is a dry run
            if not dry_run:
                processed_doc.save()
                
            processed_docs.append(processed_doc)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return processed_docs


def extract_document_sections(
    doc: Document,
    section_pattern: str = r'^##\s+(.+)$',
    include_content: bool = True,
    max_depth: int = 2
) -> Dict[str, str]:
    """
    Extract sections from an MDP document based on headers.
    
    Args:
        doc: Document to extract sections from
        section_pattern: Regex pattern to match section headers
        include_content: Whether to include section content in results
        max_depth: Maximum header depth to consider (2 = ##, 3 = ###, etc.)
        
    Returns:
        Dictionary mapping section titles to section content
    """
    sections = {}
    lines = doc.content.splitlines()
    
    current_section = None
    current_content = []
    current_depth = 0
    
    for line in lines:
        # Check for headers of different depths
        header_match = None
        matched_depth = 0
        
        for depth in range(1, max_depth + 1):
            header_prefix = '#' * depth
            pattern = f'^{header_prefix}\\s+(.+)$'
            match = re.match(pattern, line)
            if match:
                header_match = match
                matched_depth = depth
                break
        
        if header_match:
            # Save the previous section if there was one
            if current_section and include_content:
                sections[current_section] = '\n'.join(current_content).strip()
                
            # Start a new section if it's at our target depth
            section_title = header_match.group(1).strip()
            if matched_depth <= max_depth:
                current_section = section_title
                current_depth = matched_depth
                current_content = []
                
                # Always add the section to the dictionary, even if we don't include content
                if not include_content:
                    sections[current_section] = ''
                    
        elif current_section and include_content:
            # Add the line to the current section's content
            current_content.append(line)
    
    # Don't forget the last section
    if current_section and include_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def create_document_from_template(
    template_path: Union[str, Path],
    output_path: Union[str, Path],
    replacements: Dict[str, str],
    auto_metadata: bool = True,
    **metadata_values
) -> Document:
    """
    Create a new MDP document based on a template.
    
    This function reads a template file, performs string replacements,
    and creates a new document.
    
    Args:
        template_path: Path to the template file
        output_path: Path to save the new document
        replacements: Dictionary of template variables and their replacements
        auto_metadata: Whether to automatically generate metadata
        **metadata_values: Additional metadata key-value pairs
        
    Returns:
        The created Document object
    """
    # Read the template file
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    # Apply replacements
    content = template_content
    for key, value in replacements.items():
        token = f"{{{{ {key} }}}}"
        content = content.replace(token, value)
    
    # Create the document
    if auto_metadata:
        doc = Document.create_with_auto_metadata(
            content=content,
            **metadata_values
        )
    else:
        doc = Document(content=content, metadata=metadata_values)
    
    # Set the output path and save
    doc._mdp_file.path = Path(output_path)
    os.makedirs(doc._mdp_file.path.parent, exist_ok=True)
    doc.save()
    
    return doc


def merge_documents(
    docs: List[Document],
    output_path: Union[str, Path],
    title: str,
    separator: str = "\n---\n",
    include_document_titles: bool = True,
    include_metadata: bool = False,
    document_header_level: int = 2
) -> Document:
    """
    Merge multiple MDP documents into a single document.
    
    Args:
        docs: List of documents to merge
        output_path: Path to save the merged document
        title: Title for the merged document
        separator: Separator to use between documents
        include_document_titles: Whether to include document titles as headers
        include_metadata: Whether to include document metadata in the content
        document_header_level: Header level for document titles (2 = ##)
        
    Returns:
        The merged Document object
    """
    # Start with the main title
    content = f"# {title}\n\n"
    
    # Merge each document
    for i, doc in enumerate(docs):
        if i > 0:
            content += separator + "\n\n"
        
        if include_document_titles:
            doc_lines = doc.content.splitlines()
            doc_title = doc.metadata.get("title", None)
            
            # Try to extract title from content if not in metadata
            if not doc_title and doc_lines and doc_lines[0].startswith("# "):
                doc_title = doc_lines[0][2:].strip()
                doc_content_start = 1
            else:
                doc_content_start = 0
                
            if not doc_title:
                doc_title = f"Document {i+1}"
                
            # Add document title as header
            content += f"{'#' * document_header_level} {doc_title}\n\n"
            
            # Add document content, skipping its title
            while doc_content_start < len(doc_lines) and not doc_lines[doc_content_start].strip():
                doc_content_start += 1
                
            content += "\n".join(doc_lines[doc_content_start:]) + "\n"
            
        else:
            # Add full document content
            content += doc.content + "\n"
            
        # Add metadata if requested
        if include_metadata:
            content += f"\n### Metadata for {doc.metadata.get('title', f'Document {i+1}')}\n\n"
            content += "```json\n"
            content += "{\n"
            for key, value in doc.metadata.items():
                if isinstance(value, str):
                    content += f'  "{key}": "{value}",\n'
                else:
                    content += f'  "{key}": {value},\n'
            content = content.rstrip(",\n") + "\n"
            content += "}\n```\n\n"
    
    # Create merged document
    merged_doc = Document.create_with_auto_metadata(
        content=content,
        title=title,
        doc_type="merged_document",
        source_count=len(docs)
    )
    
    # Set the output path and save
    merged_doc._mdp_file.path = Path(output_path)
    os.makedirs(merged_doc._mdp_file.path.parent, exist_ok=True)
    merged_doc.save()
    
    return merged_doc


def ai_process_documents(
    source_directory: Union[str, Path],
    output_directory: Union[str, Path],
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    include_pattern: str = "*.*",
    recursive: bool = True,
    create_collection: bool = True,
    analyze_relationships: bool = True,
    enhancements: Optional[List[str]] = None
) -> Tuple[List[Document], Optional[Collection]]:
    """
    Process documents in a directory using AI capabilities.
    
    This function uses AI to extract metadata, analyze document structure,
    identify relationships, and enhance content for all supported documents
    in a directory.
    
    Args:
        source_directory: Directory containing source documents
        output_directory: Directory to save processed MDP documents
        settings: Optional AI settings to configure the processing
        api_key: Optional API key to override the default
        include_pattern: Pattern to match files
        recursive: Whether to search directories recursively
        create_collection: Whether to create a Collection
        analyze_relationships: Whether to analyze relationships between documents
        enhancements: Optional list of enhancements to apply
        
    Returns:
        Tuple of (list of processed Document objects, optional Collection)
    """
    if not AI_AVAILABLE:
        raise ImportError("AI capabilities are not available. Install the required dependencies.")
    
    # Configure AI settings if provided
    if settings:
        configure_ai(settings)
    if api_key:
        ai_settings.default_model.api_key = api_key
    
    source_dir = Path(source_directory)
    output_dir = Path(output_directory)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the document processing agent
    doc_agent = DocumentProcessingAgent()
    
    # Process all documents in the directory
    documents, collection = doc_agent.process_directory(
        directory_path=source_dir,
        recursive=recursive,
        file_pattern=include_pattern,
        create_collection=create_collection,
        analyze_relationships=analyze_relationships
    )
    
    # Apply additional enhancements if requested
    if enhancements and len(documents) > 0:
        enhancement_agent = ContentEnhancementAgent()
        
        for doc in documents:
            # Add enhanced metadata to each document
            if "summary" in enhancements:
                summary = enhancement_agent.generate_summary(doc)
                if "x_enhancements" not in doc.metadata:
                    doc.metadata["x_enhancements"] = {}
                doc.metadata["x_enhancements"]["ai_summary"] = summary
            
            if "annotations" in enhancements:
                annotations = enhancement_agent.generate_annotations(doc)
                if "x_enhancements" not in doc.metadata:
                    doc.metadata["x_enhancements"] = {}
                doc.metadata["x_enhancements"]["ai_annotations"] = annotations
            
            if "improvements" in enhancements:
                improvements = enhancement_agent.suggest_improvements(doc)
                if "x_enhancements" not in doc.metadata:
                    doc.metadata["x_enhancements"] = {}
                doc.metadata["x_enhancements"]["ai_improvements"] = improvements
    
    # Save all documents to the output directory
    for doc in documents:
        # Create a new path in the output directory
        if doc.path:
            # Maintain relative structure from source directory
            rel_path = doc.path.relative_to(source_dir) if doc.path.is_relative_to(source_dir) else doc.path.name
            new_path = output_dir / rel_path
            # Ensure the parent directory exists
            os.makedirs(new_path.parent, exist_ok=True)
        else:
            # Create a filename based on the title
            safe_title = "".join(c if c.isalnum() else "_" for c in doc.title)
            new_path = output_dir / f"{safe_title}.mdp"
        
        # Save the document
        doc.save(new_path)
    
    # If a collection was created, save a collection index
    if collection:
        collection.export(output_dir)
    
    return documents, collection


def ai_enhance_document(
    document: Document,
    enhancements: List[str] = ["tags", "summary"],
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
    api_key: Optional[str] = None
) -> Document:
    """
    Enhance a document with AI capabilities.
    
    This function uses AI to enhance an existing document with
    additional metadata, summaries, or content improvements.
    
    Args:
        document: The document to enhance
        enhancements: List of enhancements to apply
        settings: Optional AI settings to configure the processing
        api_key: Optional API key to override the default
        
    Returns:
        The enhanced document
    """
    if not AI_AVAILABLE:
        raise ImportError("AI capabilities are not available. Install the required dependencies.")
    
    # Configure AI settings if provided
    if settings:
        configure_ai(settings)
    if api_key:
        ai_settings.default_model.api_key = api_key
    
    # Apply metadata enhancements
    if any(e in enhancements for e in ["title", "tags", "summary"]):
        document.auto_enhance_metadata(
            update_title="title" in enhancements,
            update_tags="tags" in enhancements,
            update_summary="summary" in enhancements
        )
    
    # Apply additional advanced enhancements
    if any(e in enhancements for e in ["full_summary", "annotations", "improvements"]):
        enhancement_agent = ContentEnhancementAgent()
        
        # Initialize the enhancements dict if needed
        if "x_enhancements" not in document.metadata:
            document.metadata["x_enhancements"] = {}
        
        # Generate a more detailed summary
        if "full_summary" in enhancements:
            summary = enhancement_agent.generate_summary(
                document, 
                length="long"
            )
            document.metadata["x_enhancements"]["full_summary"] = summary
        
        # Generate annotations
        if "annotations" in enhancements:
            annotations = enhancement_agent.generate_annotations(document)
            document.metadata["x_enhancements"]["annotations"] = annotations
        
        # Generate improvement suggestions
        if "improvements" in enhancements:
            improvements = enhancement_agent.suggest_improvements(document)
            document.metadata["x_enhancements"]["improvements"] = improvements
    
    return document 