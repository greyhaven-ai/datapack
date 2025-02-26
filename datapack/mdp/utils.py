"""
Utility functions for working with MDP (Markdown Data Pack) files.

This module provides utility functions for working with MDP files,
such as converting between different formats and finding MDP files.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

from datapack.mdp.core import MDPFile, read_mdp, write_mdp
from datapack.mdp.metadata import create_metadata, parse_uri, is_valid_uuid


# Type for a resolver function
ResolverFunction = Callable[[str, Optional[Path]], Optional[MDPFile]]


def resolve_reference(
    reference: Dict[str, Any], 
    base_path: Optional[Path] = None,
    resolvers: Optional[List[ResolverFunction]] = None
) -> Optional[MDPFile]:
    """
    Resolve a relationship reference to an actual MDPFile.
    
    Args:
        reference: The relationship reference dictionary
        base_path: Optional base path for relative paths
        resolvers: Optional list of custom resolver functions
        
    Returns:
        The resolved MDPFile or None if not found
    """
    # Default resolvers if none provided
    if resolvers is None:
        resolvers = [
            resolve_by_path,
            resolve_by_uuid,
            resolve_by_uri
        ]
    
    # Extract the reference identifier
    if "path" in reference:
        identifier = reference["path"]
        resolver_method = resolve_by_path
    elif "id" in reference:
        identifier = reference["id"]
        resolver_method = resolve_by_uuid
    elif "uri" in reference:
        identifier = reference["uri"]
        resolver_method = resolve_by_uri
    else:
        return None
    
    # Try the specific resolver first
    result = resolver_method(identifier, base_path)
    if result:
        return result
    
    # Try all resolvers
    for resolver in resolvers:
        if resolver != resolver_method:  # Skip the one we already tried
            result = resolver(identifier, base_path)
            if result:
                return result
    
    return None


def resolve_by_path(
    path: str, 
    base_path: Optional[Path] = None
) -> Optional[MDPFile]:
    """
    Resolve a reference by file path.
    
    Args:
        path: The file path to resolve
        base_path: Optional base path for relative paths
        
    Returns:
        The resolved MDPFile or None if not found
    """
    try:
        file_path = Path(path)
        
        # If it's a relative path and base_path is provided
        if not file_path.is_absolute() and base_path:
            file_path = base_path / file_path
        
        # Try to read the file
        if file_path.exists() and file_path.is_file():
            return read_mdp(file_path)
    except (FileNotFoundError, ValueError):
        pass
    
    return None


def resolve_by_uuid(
    uuid: str, 
    base_path: Optional[Path] = None
) -> Optional[MDPFile]:
    """
    Resolve a reference by UUID.
    
    Args:
        uuid: The UUID to resolve
        base_path: Optional base path to search in
        
    Returns:
        The resolved MDPFile or None if not found
    """
    # This is a stub implementation that would need to be connected
    # to a proper UUID registry or document store
    
    # For local-only implementation, we can search for files with matching UUID
    if base_path:
        try:
            # Find all MDP files in the directory
            mdp_files = find_mdp_files(base_path, recursive=True)
            
            # Check each file for matching UUID
            for file_path in mdp_files:
                try:
                    mdp_file = read_mdp(file_path)
                    if mdp_file.metadata.get("uuid") == uuid:
                        return mdp_file
                except:
                    # Skip files with errors
                    continue
        except:
            pass
    
    return None


def resolve_by_uri(
    uri: str, 
    base_path: Optional[Path] = None
) -> Optional[MDPFile]:
    """
    Resolve a reference by URI.
    
    Args:
        uri: The URI to resolve
        base_path: Optional base path (not used for URIs)
        
    Returns:
        The resolved MDPFile or None if not found
    """
    # This is a stub implementation that would need to be connected
    # to a central registry or server
    
    # For local-only implementation, we currently can't resolve URIs
    # A full implementation would need to connect to a network service
    
    return None


def find_related_documents(
    mdp_file: MDPFile, 
    relationship_type: Optional[str] = None,
    resolvers: Optional[List[ResolverFunction]] = None
) -> List[MDPFile]:
    """
    Find related documents from an MDPFile's relationships.
    
    Args:
        mdp_file: The MDPFile to find related documents for
        relationship_type: Optional filter by relationship type
        resolvers: Optional list of resolver functions
        
    Returns:
        List of related MDPFile objects that could be resolved
    """
    results = []
    
    # Determine base path for relative references
    base_path = mdp_file.path.parent if mdp_file.path else None
    
    # Get relationships from metadata
    relationships = mdp_file.metadata.get("relationships", [])
    
    # Filter by type if specified
    if relationship_type:
        relationships = [r for r in relationships if r.get("type") == relationship_type]
    
    # Resolve each relationship
    for relationship in relationships:
        related_doc = resolve_reference(relationship, base_path, resolvers)
        if related_doc:
            results.append(related_doc)
    
    return results


def find_mdp_files(
    directory: Union[str, Path],
    recursive: bool = True
) -> List[Path]:
    """
    Find all MDP files in a directory.
    
    Args:
        directory: The directory to search in.
        recursive: Whether to search recursively in subdirectories.
    
    Returns:
        A list of paths to MDP files.
    """
    directory_path = Path(directory)
    
    if not directory_path.exists() or not directory_path.is_dir():
        raise ValueError(f"Directory not found: {directory}")
    
    mdp_files = []
    
    if recursive:
        # Search recursively
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".mdp"):
                    mdp_files.append(Path(root) / file)
    else:
        # Search only in the specified directory
        mdp_files = [
            file for file in directory_path.iterdir()
            if file.is_file() and file.suffix == ".mdp"
        ]
    
    return mdp_files


def convert_to_mdp(
    source_path: Union[str, Path],
    target_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MDPFile:
    """
    Convert a text or markdown file to an MDP file.
    
    Args:
        source_path: The path to the source file.
        target_path: The path to save the MDP file to. If None, uses the source path
                     with the extension changed to .mdp.
        metadata: Additional metadata to include in the MDP file.
    
    Returns:
        An MDPFile object representing the converted file.
    
    Raises:
        FileNotFoundError: If the source file does not exist.
        ValueError: If the source file is not a text file.
    """
    source_path = Path(source_path)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Determine the target path if not provided
    if target_path is None:
        target_path = source_path.with_suffix(".mdp")
    else:
        target_path = Path(target_path)
    
    # Read the source file
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Create metadata with defaults
    file_metadata = create_metadata(
        metadata,
        source_file=str(source_path.name),
        source_type=source_path.suffix[1:],  # Remove the leading dot
    )
    
    # Write the MDP file
    return write_mdp(target_path, file_metadata, content)


def batch_convert_to_mdp(
    source_directory: Union[str, Path],
    target_directory: Optional[Union[str, Path]] = None,
    file_extensions: List[str] = [".txt", ".md", ".markdown"],
    recursive: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -> List[MDPFile]:
    """
    Convert multiple text or markdown files to MDP files.
    
    Args:
        source_directory: The directory containing the source files.
        target_directory: The directory to save the MDP files to. If None, uses the source directory.
        file_extensions: The file extensions to convert.
        recursive: Whether to search recursively in subdirectories.
        metadata: Additional metadata to include in all MDP files.
    
    Returns:
        A list of MDPFile objects representing the converted files.
    
    Raises:
        ValueError: If the source directory does not exist.
    """
    source_dir = Path(source_directory)
    
    if not source_dir.exists() or not source_dir.is_dir():
        raise ValueError(f"Source directory not found: {source_dir}")
    
    # Determine the target directory if not provided
    if target_directory is None:
        target_dir = source_dir
    else:
        target_dir = Path(target_directory)
        os.makedirs(target_dir, exist_ok=True)
    
    converted_files = []
    
    # Find all files with the specified extensions
    if recursive:
        # Search recursively
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                if any(file.endswith(ext) for ext in file_extensions):
                    # Determine the target path
                    rel_path = file_path.relative_to(source_dir)
                    target_path = target_dir / rel_path.with_suffix(".mdp")
                    
                    # Create the target directory if it doesn't exist
                    os.makedirs(target_path.parent, exist_ok=True)
                    
                    # Convert the file
                    try:
                        mdp_file = convert_to_mdp(file_path, target_path, metadata)
                        converted_files.append(mdp_file)
                    except Exception as e:
                        print(f"Error converting {file_path}: {e}")
    else:
        # Search only in the specified directory
        for file_path in source_dir.iterdir():
            if file_path.is_file() and any(file_path.suffix == ext for ext in file_extensions):
                # Determine the target path
                target_path = target_dir / file_path.with_suffix(".mdp").name
                
                # Convert the file
                try:
                    mdp_file = convert_to_mdp(file_path, target_path, metadata)
                    converted_files.append(mdp_file)
                except Exception as e:
                    print(f"Error converting {file_path}: {e}")
    
    return converted_files


def find_collection_members(
    directory: Union[str, Path],
    collection_name: str,
    collection_id: Optional[str] = None,
    recursive: bool = True,
) -> List[MDPFile]:
    """
    Find all members of a collection in a directory.
    
    Args:
        directory: The directory to search in
        collection_name: The name of the collection to find
        collection_id: Optional collection ID to match
        recursive: Whether to search recursively
        
    Returns:
        List of MDPFile objects that are members of the collection
    """
    results = []
    
    # Find all MDP files in the directory
    mdp_files = find_mdp_files(directory, recursive=recursive)
    
    # Check each file for collection membership
    for file_path in mdp_files:
        try:
            mdp_file = read_mdp(file_path)
            metadata = mdp_file.metadata
            
            # Check if the file belongs to the specified collection
            if metadata.get("collection") == collection_name:
                # If collection_id is specified, check that too
                if collection_id is None or metadata.get("collection_id") == collection_id:
                    results.append(mdp_file)
        except:
            # Skip files with errors
            continue
    
    # Sort by position if available
    results.sort(key=lambda x: x.metadata.get("position", float('inf')))
    
    return results


def create_collection(
    directory: Union[str, Path],
    collection_name: str,
    collection_id: Optional[str] = None,
    documents: Optional[List[Dict[str, Any]]] = None
) -> List[MDPFile]:
    """
    Create a collection of MDP files.
    
    Args:
        directory: The directory to create the collection in
        collection_name: The name of the collection
        collection_id: Optional unique identifier for the collection
        documents: List of document specifications with metadata and content
        
    Returns:
        List of created MDPFile objects
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        os.makedirs(directory_path)
    
    results = []
    
    # Create documents if provided
    if documents:
        for position, doc_spec in enumerate(documents):
            # Extract metadata and content
            metadata = doc_spec.get("metadata", {})
            content = doc_spec.get("content", "")
            filename = doc_spec.get("filename")
            
            # Ensure the document has collection information
            metadata["collection"] = collection_name
            if collection_id:
                metadata["collection_id"] = collection_id
            metadata["position"] = position
            
            # Create a filename if not provided
            if not filename:
                title = metadata.get("title", f"document_{position}")
                # Convert title to filename-friendly format
                filename = title.lower().replace(" ", "_") + ".mdp"
            
            # Ensure filename has .mdp extension
            if not filename.endswith(".mdp"):
                filename += ".mdp"
            
            # Create the file
            file_path = directory_path / filename
            mdp_file = write_mdp(file_path, metadata, content)
            results.append(mdp_file)
    
    return results


def get_collection_hierarchy(
    mdp_file: MDPFile,
    resolvers: Optional[List[ResolverFunction]] = None
) -> Dict[str, Any]:
    """
    Get the hierarchy information for a document in a collection.
    
    Args:
        mdp_file: The MDPFile to get hierarchy for
        resolvers: Optional list of resolver functions
        
    Returns:
        Dictionary with hierarchy information (parent, children, siblings)
    """
    result = {
        "parent": None,
        "children": [],
        "siblings": [],
        "position": mdp_file.metadata.get("position"),
        "collection": mdp_file.metadata.get("collection"),
        "collection_id": mdp_file.metadata.get("collection_id")
    }
    
    # Get parent document
    parent_docs = find_related_documents(mdp_file, relationship_type="parent", resolvers=resolvers)
    if parent_docs:
        result["parent"] = parent_docs[0]
    
    # Get child documents
    result["children"] = find_related_documents(mdp_file, relationship_type="child", resolvers=resolvers)
    
    # If we have a parent, get siblings
    if result["parent"]:
        siblings = find_related_documents(result["parent"], relationship_type="child", resolvers=resolvers)
        # Remove self from siblings
        result["siblings"] = [doc for doc in siblings if doc.metadata.get("uuid") != mdp_file.metadata.get("uuid")]
    # Otherwise try to find siblings by collection membership
    elif mdp_file.path and mdp_file.metadata.get("collection"):
        collection_members = find_collection_members(
            mdp_file.path.parent,
            mdp_file.metadata["collection"],
            mdp_file.metadata.get("collection_id"),
            recursive=True
        )
        # Remove self from collection members
        result["siblings"] = [doc for doc in collection_members if doc.metadata.get("uuid") != mdp_file.metadata.get("uuid")]
    
    return result 


def extract_metadata_from_content(
    content: str,
    extract_title: bool = True,
    extract_tags: bool = True,
    extract_summary: bool = True,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract metadata from document content using NLP techniques.
    
    This function analyzes the document content and automatically generates
    metadata such as title, tags, and summary using basic NLP techniques.
    If more advanced extraction is needed, an external model can be specified.
    
    Args:
        content: The document content to analyze
        extract_title: Whether to extract a title
        extract_tags: Whether to extract tags/keywords
        extract_summary: Whether to extract a summary
        model: Optional name of an external model to use for extraction
        
    Returns:
        A dictionary containing extracted metadata
    """
    metadata = {}
    
    # Basic title extraction (first heading)
    if extract_title:
        heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if heading_match:
            metadata["title"] = heading_match.group(1).strip()
    
    # Basic tag extraction (frequency-based keywords)
    if extract_tags:
        # Simple word frequency analysis
        # Skip stopwords and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        stopwords = {
            'the', 'and', 'or', 'if', 'this', 'that', 'with', 'from', 'for',
            'are', 'was', 'were', 'have', 'has', 'had', 'not', 'but', 'what',
            'when', 'where', 'how', 'why', 'which', 'who', 'whom'
        }
        words = [word for word in words if word not in stopwords]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Select top keywords (max 5)
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        if keywords:
            metadata["tags"] = [k[0] for k in keywords]
    
    # Basic summary extraction (first paragraph or first few sentences)
    if extract_summary:
        # Remove headings and other Markdown syntax
        cleaned_content = re.sub(r"^#.+$", "", content, flags=re.MULTILINE)
        cleaned_content = re.sub(r"[*_~`]", "", cleaned_content)
        
        # Find first paragraph
        paragraphs = [p.strip() for p in cleaned_content.split("\n\n") if p.strip()]
        if paragraphs:
            # Get the first paragraph, limit to 200 chars
            first_para = paragraphs[0]
            summary = first_para[:200]
            if len(first_para) > 200:
                summary += "..."
            metadata["description"] = summary
    
    # If an external model is specified, use it for more advanced extraction
    if model:
        try:
            # Use our AI-based metadata extraction if available
            try:
                # Import dynamically to avoid circular imports
                from datapack.ai.extractors import MetadataExtractor
                
                # Create extractor with the specified model
                extractor = MetadataExtractor(model=model)
                
                # Extract metadata
                extracted = extractor.extract_metadata(
                    content=content,
                    extract_title=extract_title,
                    extract_tags=extract_tags,
                    extract_summary=extract_summary
                )
                
                # Apply extracted metadata
                if extract_title and extracted.title:
                    metadata["title"] = extracted.title
                
                if extract_tags and extracted.tags:
                    metadata["tags"] = extracted.tags
                
                if extract_summary and extracted.description:
                    metadata["description"] = extracted.description
                
                # Mark as AI-generated
                metadata["ai_generated"] = True
                metadata["ai_model"] = model
                
                return metadata
                
            except ImportError:
                # Fall back to basic extraction if AI module not available
                pass
                
            # Legacy model integration (fallback)
            if model == "openai":
                # Example integration with OpenAI's API (not implemented)
                metadata["model_generated"] = True
            elif model == "local":
                # Example integration with a local model (not implemented)
                metadata["model_generated"] = True
        except Exception as e:
            # Log but don't fail if model integration fails
            print(f"Warning: Model-based metadata extraction failed: {e}")
    
    return metadata 