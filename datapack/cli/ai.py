"""
Command-line interface for datapack AI functionality.

This module provides CLI commands for AI-powered document processing.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import asyncio
import datetime

from mdp import Document

from .utils import (
    determine_format_type,
    get_output_path,
    parse_key_value_string,
    get_supported_format_types
)

# Check for AI support
try:
    from datapack.ai.models import (
        AIModelConfig, 
        DocumentMetadata, 
        ExtractedMetadata,
        DocumentStructure
    )
    from datapack.ai.extractors import (
        MetadataExtractor,
        ContentStructureExtractor,
        RelationshipExtractor,
        PDFExtractor
    )
    from datapack.ai.agents import (
        DocumentProcessingAgent,
        ContentEnhancementAgent,
        CollectionCreationAgent
    )
    from datapack.ai.structured_output import (
        StructuredOutputGenerator
    )
    AI_SUPPORT = True
except ImportError:
    AI_SUPPORT = False


def _check_ai_support():
    """
    Check if AI support is available.
    
    Raises:
        ImportError: If AI support is not available
    """
    if not AI_SUPPORT:
        raise ImportError(
            "AI support is not available. Install the required AI dependencies:\n"
            "pip install datapack[ai]"
        )


def extract_metadata(
    input_path: str,
    output_path: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    format_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Extract metadata from a document using AI.
    
    Args:
        input_path: Path to the input file
        output_path: Optional path to save extracted metadata as JSON
        model_config: Configuration for the AI model
        format_type: Type of the input file (optional, auto-detected if not provided)
        **kwargs: Additional arguments for the extractor
        
    Returns:
        Dictionary containing extracted metadata
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Determine format type if not provided
    if not format_type:
        try:
            format_type = determine_format_type(input_path)
        except ValueError:
            # Default to text for unknown file types
            format_type = 'text'
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.0)),
        api_key=model_config.get('api_key')
    )
    
    # Create and run the extractor
    extractor = MetadataExtractor(model_config=ai_config)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata = extractor.extract(content, format_type=format_type, **kwargs)
    
    # Save metadata to file if output path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.model_dump(), f, indent=2)
    
    return metadata.model_dump()


def extract_structure(
    input_path: str,
    output_path: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    format_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Extract document structure using AI.
    
    Args:
        input_path: Path to the input file
        output_path: Optional path to save extracted structure as JSON
        model_config: Configuration for the AI model
        format_type: Type of the input file (optional, auto-detected if not provided)
        **kwargs: Additional arguments for the extractor
        
    Returns:
        Dictionary containing the document structure
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Determine format type if not provided
    if not format_type:
        try:
            format_type = determine_format_type(input_path)
        except ValueError:
            # Default to text for unknown file types
            format_type = 'text'
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.0)),
        api_key=model_config.get('api_key')
    )
    
    # Create and run the extractor
    extractor = ContentStructureExtractor(model_config=ai_config)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    structure = extractor.extract(content, format_type=format_type, **kwargs)
    
    # Save structure to file if output path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structure.model_dump(), f, indent=2)
    
    return structure.model_dump()


def enhance_document(
    input_path: str,
    output_path: str,
    model_config: Optional[Dict[str, Any]] = None,
    format_type: Optional[str] = None,
    extract_metadata: bool = True,
    extract_structure: bool = True,
    extract_relationships: bool = False,
    **kwargs
) -> Document:
    """
    Enhance a document using AI processing.
    
    Args:
        input_path: Path to the input file
        output_path: Path to save the enhanced MDP file
        model_config: Configuration for the AI model
        format_type: Type of the input file (optional, auto-detected if not provided)
        extract_metadata: Whether to extract metadata
        extract_structure: Whether to extract document structure
        extract_relationships: Whether to extract relationships
        **kwargs: Additional arguments for the agent
        
    Returns:
        The enhanced MDP Document
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Determine format type if not provided
    if not format_type:
        try:
            format_type = determine_format_type(input_path)
        except ValueError:
            # Default to text for unknown file types
            format_type = 'text'
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.0)),
        api_key=model_config.get('api_key')
    )
    
    # Create and configure the agent
    agent = DocumentProcessingAgent(model_config=ai_config)
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process the document
    document = agent.process(
        content,
        format_type=format_type,
        extract_metadata=extract_metadata,
        extract_structure=extract_structure,
        extract_relationships=extract_relationships,
        **kwargs
    )
    
    # Save to MDP file
    document.save(output_path)
    
    return document


async def create_collection(
    input_paths: List[str],
    output_dir: str,
    collection_name: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    organization_strategy: str = "auto",
    create_parent_document: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a collection from multiple documents using AI.
    
    Args:
        input_paths: List of paths to input files
        output_dir: Directory to save the collection
        collection_name: Optional name for the collection
        model_config: Configuration for the AI model
        organization_strategy: Strategy for organizing documents
        create_parent_document: Whether to create a parent document
        **kwargs: Additional arguments for the agent
        
    Returns:
        Dictionary with information about the created collection
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.0)),
        api_key=model_config.get('api_key')
    )
    
    # Create the collection agent
    agent = CollectionCreationAgent(ai_config)
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create the collection
    collection = await agent.create_collection_from_documents(
        documents=input_paths,
        collection_name=collection_name,
        base_path=output_path,
        organization_strategy=organization_strategy,
        create_parent_document=create_parent_document,
        extract_relationships=True,
        save_documents=True,
        **kwargs
    )
    
    # Prepare response
    parent_doc = None
    if create_parent_document and collection.documents:
        parent_doc = collection.documents[0]
    
    result = {
        "collection_name": collection.name,
        "collection_id": collection.metadata.get("collection_id", ""),
        "document_count": len(collection.documents),
        "output_directory": str(output_path / collection.name),
        "parent_document": parent_doc.title if parent_doc else None,
        "parent_document_path": str(parent_doc.path) if parent_doc and parent_doc.path else None,
        "success": True
    }
    
    return result


async def organize_documents_by_theme(
    input_paths: List[str],
    output_dir: str,
    model_config: Optional[Dict[str, Any]] = None,
    max_collections: int = 5,
    min_documents_per_collection: int = 2,
    create_parent_documents: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Organize multiple documents into thematic collections using AI.
    
    Args:
        input_paths: List of paths to input files
        output_dir: Directory to save the collections
        model_config: Configuration for the AI model
        max_collections: Maximum number of collections to create
        min_documents_per_collection: Minimum documents per collection
        create_parent_documents: Whether to create parent documents
        **kwargs: Additional arguments for the agent
        
    Returns:
        Dictionary with information about the created collections
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.0)),
        api_key=model_config.get('api_key')
    )
    
    # Create the collection agent
    agent = CollectionCreationAgent(ai_config)
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Organize documents into collections
    collections = await agent.organize_documents_by_theme(
        documents=input_paths,
        base_path=output_path,
        max_collections=max_collections,
        min_documents_per_collection=min_documents_per_collection,
        create_parent_documents=create_parent_documents,
        save_documents=True,
        **kwargs
    )
    
    # Prepare response
    result = {
        "collections": [
            {
                "name": coll.name,
                "document_count": len(coll.documents),
                "directory": str(output_path / coll.name)
            }
            for coll in collections
        ],
        "total_collections": len(collections),
        "total_documents": sum(len(coll.documents) for coll in collections),
        "output_directory": str(output_path),
        "success": True
    }
    
    return result


async def analyze_collection_relationships(
    collection_paths: List[str],
    output_path: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze relationships between collections using AI.
    
    Args:
        collection_paths: List of paths to collection parent documents
        output_path: Optional path to save the relationship analysis
        model_config: Configuration for the AI model
        **kwargs: Additional arguments for the agent
        
    Returns:
        Dictionary with information about the analysis results
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.1)),
        api_key=model_config.get('api_key')
    )
    
    # Create the collection agent
    agent = CollectionCreationAgent(ai_config)
    
    # Convert paths to Path objects
    collection_docs = [Path(path) for path in collection_paths]
    
    # Analyze relationships
    relationships = await agent.analyze_collection_relationships(collection_docs)
    
    # Generate relationship report
    report = "# Collection Relationships Analysis\n\n"
    report += f"Analysis of {len(collection_docs)} collections\n\n"
    
    for relationship in relationships:
        report += f"## {relationship.type}\n\n"
        report += f"**{relationship.source}** → **{relationship.target}**\n\n"
        report += f"{relationship.description}\n\n"
        if relationship.confidence:
            report += f"Confidence: {relationship.confidence:.2f}\n\n"
    
    # Save report if output path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    # Prepare response
    result = {
        "collection_count": len(collection_docs),
        "relationship_count": len(relationships),
        "relationships": [
            {
                "type": rel.type,
                "source": rel.source,
                "target": rel.target,
                "description": rel.description,
                "confidence": rel.confidence
            }
            for rel in relationships
        ],
        "report": report,
        "output_path": output_path,
        "success": True
    }
    
    return result


def parse_model_config(config_str: str) -> Dict[str, Any]:
    """
    Parse AI model configuration from a string.
    
    Args:
        config_str: Configuration string in the format "provider=google,model=gemini-1.5-flash,temperature=0.2"
        
    Returns:
        Dictionary of model configuration
    """
    return parse_key_value_string(config_str)


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """
    Set up the AI CLI parser.
    
    Args:
        parser: The argparse parser to set up
    """
    subparsers = parser.add_subparsers(dest='command', help='AI command to run')
    
    # Metadata extraction
    metadata_parser = subparsers.add_parser(
        'extract-metadata',
        help='Extract metadata from a document using AI'
    )
    metadata_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input file'
    )
    metadata_parser.add_argument(
        '-o', '--output',
        help='Path to save the extracted metadata as JSON (optional)'
    )
    metadata_parser.add_argument(
        '--format',
        choices=get_supported_format_types(),
        help='Input file format (auto-detected if not specified)'
    )
    metadata_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: model=gemini-1.5-flash,temperature=0.2)'
    )
    
    # Structure extraction
    structure_parser = subparsers.add_parser(
        'extract-structure',
        help='Extract document structure using AI'
    )
    structure_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input file'
    )
    structure_parser.add_argument(
        '-o', '--output',
        help='Path to save extracted structure as JSON'
    )
    structure_parser.add_argument(
        '-f', '--format',
        choices=get_supported_format_types(),
        help='Format of the input file (default: determined from file extension)'
    )
    structure_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: provider=google,model=gemini-1.5-flash,temperature=0.2)'
    )
    
    # Document enhancement
    enhance_parser = subparsers.add_parser(
        'enhance',
        help='Enhance a document using AI processing'
    )
    enhance_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input file'
    )
    enhance_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path to save the enhanced MDP file'
    )
    enhance_parser.add_argument(
        '-f', '--format',
        choices=get_supported_format_types(),
        help='Format of the input file (default: determined from file extension)'
    )
    enhance_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: provider=google,model=gemini-1.5-flash,temperature=0.2)'
    )
    enhance_parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Skip metadata extraction'
    )
    enhance_parser.add_argument(
        '--no-structure',
        action='store_true',
        help='Skip structure extraction'
    )
    enhance_parser.add_argument(
        '--extract-relationships',
        action='store_true',
        help='Extract relationships between document elements'
    )
    
    # Collection creation
    collection_parser = subparsers.add_parser(
        'create-collection',
        help='Create a collection from multiple documents using AI'
    )
    collection_parser.add_argument(
        '-i', '--input',
        required=True,
        nargs='+',
        help='Paths to input files (accepts multiple files)'
    )
    collection_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Directory to save the collection'
    )
    collection_parser.add_argument(
        '-n', '--name',
        help='Name for the collection (default: auto-generated)'
    )
    collection_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: provider=google,model=gemini-1.5-flash,temperature=0.2)'
    )
    collection_parser.add_argument(
        '--strategy',
        choices=['auto', 'thematic', 'chronological', 'hierarchical'],
        default='auto',
        help='Strategy for organizing documents (default: auto)'
    )
    collection_parser.add_argument(
        '--no-parent-document',
        action='store_true',
        help='Skip creation of parent document'
    )
    
    # Theme-based organization
    theme_parser = subparsers.add_parser(
        'organize-by-theme',
        help='Organize documents into thematic collections using AI'
    )
    theme_parser.add_argument(
        '-i', '--input',
        required=True,
        nargs='+',
        help='Paths to input files (accepts multiple files)'
    )
    theme_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Directory to save the collections'
    )
    theme_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: provider=google,model=gemini-1.5-flash,temperature=0.2)'
    )
    theme_parser.add_argument(
        '--max-collections',
        type=int,
        default=5,
        help='Maximum number of collections to create (default: 5)'
    )
    theme_parser.add_argument(
        '--min-documents',
        type=int,
        default=2,
        help='Minimum documents per collection (default: 2)'
    )
    theme_parser.add_argument(
        '--no-parent-documents',
        action='store_true',
        help='Skip creation of parent documents'
    )
    
    # Collection analysis
    analysis_parser = subparsers.add_parser(
        'analyze-collections',
        help='Analyze relationships between collections using AI'
    )
    analysis_parser.add_argument(
        '-i', '--input',
        required=True,
        nargs='+',
        help='Paths to collection parent documents (accepts multiple files)'
    )
    analysis_parser.add_argument(
        '-o', '--output',
        help='Path to save the relationship analysis report'
    )
    analysis_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: provider=google,model=gemini-1.5-flash,temperature=0.1)'
    )

    # Document content update
    update_parser = subparsers.add_parser(
        'update-document',
        help='Update document content using AI'
    )
    update_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input document'
    )
    update_parser.add_argument(
        '-o', '--output',
        help='Path to save the updated document (optional)'
    )
    update_parser.add_argument(
        '--content',
        required=True,
        help='New content to add or replace'
    )
    update_parser.add_argument(
        '--section',
        help='Section identifier to replace (e.g., "## Introduction")'
    )
    update_parser.add_argument(
        '--replace-entire',
        action='store_true',
        help='Replace the entire document content'
    )
    update_parser.add_argument(
        '--track-changes',
        action='store_true',
        help='Track changes in metadata context field'
    )
    update_parser.add_argument(
        '--change-summary',
        help='Custom summary of changes (used with --track-changes)'
    )
    update_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: model=gemini-2.0-flash,temperature=0.2)'
    )
    
    # Add context to document
    context_parser = subparsers.add_parser(
        'add-context',
        help='Add contextual information to a document'
    )
    context_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input document'
    )
    context_parser.add_argument(
        '-o', '--output',
        help='Path to save the updated document (optional)'
    )
    context_parser.add_argument(
        '--context',
        required=True,
        help='Contextual information to add'
    )
    context_parser.add_argument(
        '--position',
        choices=['start', 'end'],
        default='end',
        help='Where to add context (default: end)'
    )
    context_parser.add_argument(
        '--section',
        help='Section identifier to add context to (overrides position)'
    )
    context_parser.add_argument(
        '--as-comment',
        action='store_true',
        help='Format context as a Markdown comment'
    )
    context_parser.add_argument(
        '--track-changes',
        action='store_true',
        help='Track changes in metadata context field'
    )
    context_parser.add_argument(
        '--change-summary',
        help='Custom summary of changes (used with --track-changes)'
    )
    context_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: model=gemini-1.5-flash,temperature=0.2)'
    )
    
    # Query document content
    query_parser = subparsers.add_parser(
        'query-document',
        help='Query document content for specific information'
    )
    query_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input document'
    )
    query_parser.add_argument(
        '--query',
        required=True,
        help='Query or question about the document'
    )
    query_parser.add_argument(
        '--section',
        help='Optional section to limit search to'
    )
    query_parser.add_argument(
        '--max-context',
        type=int,
        default=1000,
        help='Maximum context length to return (default: 1000)'
    )
    query_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: model=gemini-1.5-flash,temperature=0.2)'
    )
    
    # Modify collection
    modify_collection_parser = subparsers.add_parser(
        'modify-collection',
        help='Modify a collection by adding or removing documents'
    )
    modify_collection_parser.add_argument(
        '-c', '--collection',
        required=True,
        help='Path to the collection parent document'
    )
    modify_collection_parser.add_argument(
        '--action',
        choices=['add', 'remove'],
        required=True,
        help='Action to perform (add or remove documents)'
    )
    modify_collection_parser.add_argument(
        '-d', '--documents',
        required=True,
        nargs='+',
        help='Paths to documents to add or remove'
    )
    modify_collection_parser.add_argument(
        '--no-update-relationships',
        action='store_true',
        help='Skip updating relationships between documents'
    )
    modify_collection_parser.add_argument(
        '--no-update-parent',
        action='store_true',
        help='Skip updating the parent document'
    )
    modify_collection_parser.add_argument(
        '--model-config',
        help='AI model configuration (format: model=gemini-1.5-flash,temperature=0.2)'
    )


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the datapack AI CLI.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description='Datapack AI Functionality')
    setup_parser(parser)
    
    args = parser.parse_args(args)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        parsed_args = args
        
        if parsed_args.command == 'extract-metadata':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Extract metadata
            metadata = extract_metadata(
                input_path=parsed_args.input,
                output_path=parsed_args.output,
                model_config=model_config,
                format_type=parsed_args.format
            )
            
            print(f"Extracted metadata from {parsed_args.input}")
            if parsed_args.output:
                print(f"Saved metadata to {parsed_args.output}")
                
            # Print important metadata fields
            for key in ['title', 'author', 'description', 'date', 'tags']:
                if key in metadata and metadata[key]:
                    print(f"{key.capitalize()}: {metadata[key]}")

        elif parsed_args.command == 'extract-structure':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Extract structure
            structure = extract_structure(
                input_path=parsed_args.input,
                output_path=parsed_args.output,
                model_config=model_config,
                format_type=parsed_args.format
            )
            
            if not parsed_args.output:
                # Print structure to console if no output path is provided
                print(json.dumps(structure, indent=2))
            
            print(f"Extracted structure from {parsed_args.input}")
            if parsed_args.output:
                print(f"Saved structure to {parsed_args.output}")
            
        elif parsed_args.command == 'enhance':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Enhance document
            document = enhance_document(
                input_path=parsed_args.input,
                output_path=parsed_args.output,
                model_config=model_config,
                format_type=parsed_args.format,
                extract_metadata=not parsed_args.no_metadata,
                extract_structure=not parsed_args.no_structure,
                extract_relationships=parsed_args.extract_relationships
            )
            
            print(f"Enhanced {parsed_args.input} using AI")
            print(f"Saved enhanced document to {parsed_args.output}")
            print(f"Document ID: {document.id}")
            print(f"Title: {document.title}")
            
        elif parsed_args.command == 'create-collection':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Create collection asynchronously
            result = asyncio.run(create_collection(
                input_paths=parsed_args.input,
                output_dir=parsed_args.output,
                collection_name=parsed_args.name,
                model_config=model_config,
                organization_strategy=parsed_args.strategy,
                create_parent_document=not parsed_args.no_parent_document
            ))
            
            print(f"Created collection '{result['collection_name']}' with {result['document_count']} documents")
            print(f"Collection ID: {result['collection_id']}")
            print(f"Saved to: {result['output_directory']}")
            if result['parent_document']:
                print(f"Parent document: {result['parent_document']}")
                print(f"Parent document path: {result['parent_document_path']}")
                
        elif parsed_args.command == 'organize-by-theme':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Organize documents by theme asynchronously
            result = asyncio.run(organize_documents_by_theme(
                input_paths=parsed_args.input,
                output_dir=parsed_args.output,
                model_config=model_config,
                max_collections=parsed_args.max_collections,
                min_documents_per_collection=parsed_args.min_documents,
                create_parent_documents=not parsed_args.no_parent_documents
            ))
            
            print(f"Created {result['total_collections']} collections with a total of {result['total_documents']} documents")
            print(f"Collections saved to: {result['output_directory']}")
            
            for i, collection in enumerate(result['collections']):
                print(f"Collection {i+1}: {collection['name']} ({collection['document_count']} documents)")
                print(f"  Directory: {collection['directory']}")
                
        elif parsed_args.command == 'analyze-collections':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Analyze collection relationships asynchronously
            result = asyncio.run(analyze_collection_relationships(
                collection_paths=parsed_args.input,
                output_path=parsed_args.output,
                model_config=model_config
            ))
            
            print(f"Analyzed relationships between {result['collection_count']} collections")
            print(f"Found {result['relationship_count']} relationships")
            
            if parsed_args.output:
                print(f"Saved relationship analysis to: {parsed_args.output}")
            else:
                print("\nRelationship Analysis Report:")
                print("-----------------------------")
                print(result['report'])
                
        elif parsed_args.command == 'update-document':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Set position from section if provided
            section = parsed_args.section
            
            # Update document asynchronously
            result = asyncio.run(update_document_content(
                input_path=parsed_args.input,
                new_content=parsed_args.content,
                output_path=parsed_args.output,
                section_identifier=section,
                replace_entire_content=parsed_args.replace_entire,
                track_changes=parsed_args.track_changes,
                change_summary=parsed_args.change_summary,
                model_config=model_config
            ))
            
            print(f"Updated document content in {parsed_args.input}")
            if "action" in result:
                if result["action"] == "section_replaced":
                    print(f"Replaced section '{result['section']}'")
                elif result["action"] == "content_replaced":
                    print("Replaced entire document content")
                elif result["action"] == "content_appended":
                    print("Appended content to document")
            
            if result.get("metadata_updated"):
                print("Updated document metadata context with change information")
                
            if parsed_args.output:
                print(f"Saved document to {parsed_args.output}")
                
            print(f"Original length: {result['original_length']} characters")
            print(f"New length: {result['new_length']} characters")
            print(f"Difference: {result['difference']} characters")
            
        elif parsed_args.command == 'add-context':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Set position from section if provided
            position = parsed_args.section if parsed_args.section else parsed_args.position
            
            # Add context asynchronously
            result = asyncio.run(add_document_context(
                input_path=parsed_args.input,
                context=parsed_args.context,
                output_path=parsed_args.output,
                position=position,
                format_as_comment=parsed_args.as_comment,
                track_changes=parsed_args.track_changes,
                change_summary=parsed_args.change_summary,
                model_config=model_config
            ))
            
            print(f"Added context to document {parsed_args.input}")
            if "action" in result:
                if result["action"] == "context_added_to_start":
                    print("Added context to the start of the document")
                elif result["action"] == "context_added_to_end":
                    print("Added context to the end of the document")
                elif result["action"] == "context_added_to_section":
                    print(f"Added context to section '{result['section']}'")
            
            if result.get("metadata_updated"):
                print("Updated document metadata context with change information")
                
            if parsed_args.output:
                print(f"Saved document to {parsed_args.output}")
                
            print(f"Added {result['context_length']} characters of context")
            print(f"New document length: {result['new_length']} characters")
            
        elif parsed_args.command == 'query-document':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Query document asynchronously
            result = asyncio.run(query_document_content(
                input_path=parsed_args.input,
                query=parsed_args.query,
                section=parsed_args.section,
                max_context_length=parsed_args.max_context,
                model_config=model_config
            ))
            
            print(f"\nQuery: {result['query']}")
            print(f"Document: {result['document_title']}")
            if parsed_args.section:
                print(f"Section: {parsed_args.section}")
            print(f"Relevance score: {result['relevance_score']:.2f}")
            print("\nRelevant context:")
            print("-" * 40)
            print(result['context'])
            print("-" * 40)
            
        elif parsed_args.command == 'modify-collection':
            # Parse model configuration
            model_config = {}
            if parsed_args.model_config:
                model_config = parse_model_config(parsed_args.model_config)
            
            # Modify collection asynchronously
            result = asyncio.run(modify_collection_documents(
                collection_path=parsed_args.collection,
                action=parsed_args.action,
                document_paths=parsed_args.documents,
                update_relationships=not parsed_args.no_update_relationships,
                update_parent_document=not parsed_args.no_update_parent,
                model_config=model_config
            ))
            
            print(f"Modified collection {parsed_args.collection}")
            print(f"Action: {result['action']}")
            print(f"Initial document count: {result['initial_document_count']}")
            print(f"Final document count: {result['final_document_count']}")
            print(f"Documents processed: {result['processed_count']}")
            
            if result.get('failed_paths'):
                print("\nFailed paths:")
                for fail in result['failed_paths']:
                    print(f"  - {fail['path']}: {fail['reason']}")
            
            if result.get('parent_document_updated'):
                print(f"\nUpdated parent document: {result['parent_document_updated']}")
        
        else:
            parser.print_help()
            return 1
        
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


async def update_document_content(
    input_path: str,
    new_content: str,
    output_path: Optional[str] = None,
    section_identifier: Optional[str] = None,
    replace_entire_content: bool = False,
    track_changes: bool = False,
    change_summary: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update document content using AI.
    
    Args:
        input_path: Path to the input file
        new_content: New content to add or replace
        output_path: Optional path to save the updated document
        section_identifier: Optional section to replace
        replace_entire_content: Whether to replace the entire content
        track_changes: Whether to track changes in metadata context field
        change_summary: Custom summary of changes (used with track_changes)
        model_config: Configuration for the AI model
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with update results
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Load the document
    document = Document.from_file(input_path)
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.1)),
        api_key=model_config.get('api_key')
    )
    
    # Create the agent
    agent = ContentEnhancementAgent(model_config=ai_config)
    
    # Create dependencies for the document
    deps = DocumentDependencies(
        document=document,
        model_name=ai_config.model_name,
        provider=ai_config.provider,
        temperature=ai_config.temperature,
        api_key=ai_config.api_key
    )
    
    # Create context with the document
    ctx = RunContext(deps)
    
    # Update the document content
    from datapack.ai.tools import update_document_content as update_content_tool
    result = await update_content_tool(
        ctx,
        new_content=new_content,
        section_identifier=section_identifier,
        replace_entire_content=replace_entire_content
    )
    
    # Update metadata context field if requested
    if track_changes:
        # Get the current context field or initialize it
        context_field = document.metadata.get("context", "")
        
        # Get current date in ISO format
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Determine the action description based on result
        action_description = ""
        if result.get("action") == "section_replaced":
            action_description = f"Updated section '{result.get('section', 'unknown')}'"
        elif result.get("action") == "content_replaced":
            action_description = "Replaced entire document content"
        elif result.get("action") == "content_appended":
            action_description = "Appended content to document"
        else:
            action_description = "Updated document content"
        
        # Format the change entry
        change_entry = f"\n\n[{current_date}] {change_summary or action_description}"
        
        # Append to the context field
        if context_field:
            document.metadata["context"] = context_field + change_entry
        else:
            document.metadata["context"] = f"Document history:\n{change_entry.lstrip()}"
        
        result["metadata_updated"] = True
    
    # Save to output path if provided
    if output_path:
        document.save(output_path)
        result["saved_to"] = output_path
    else:
        # Save in place
        document.save()
    
    return result


async def add_document_context(
    input_path: str,
    context: str,
    output_path: Optional[str] = None,
    position: str = "end",
    format_as_comment: bool = False,
    track_changes: bool = False,
    change_summary: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Add context to a document using AI.
    
    Args:
        input_path: Path to the input file
        context: Contextual information to add
        output_path: Optional path to save the updated document
        position: Where to add context (start, end, or section identifier)
        format_as_comment: Whether to format as Markdown comment
        track_changes: Whether to track changes in metadata context field
        change_summary: Custom summary of changes (used with track_changes)
        model_config: Configuration for the AI model
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with context addition results
        
    Raises:
        ImportError: If AI support is not available
    """
    _check_ai_support()
    
    # Load the document
    document = Document.from_file(input_path)
    
    # Configure the AI model
    ai_config = AIModelConfig(
        model_name=model_config.get('model', 'gemini-1.5-flash'),
        provider=model_config.get('provider', 'google'),
        temperature=float(model_config.get('temperature', 0.1)),
        api_key=model_config.get('api_key')
    )
    
    # Create the agent
    agent = ContentEnhancementAgent(model_config=ai_config)
    
    # Create dependencies for the document
    deps = DocumentDependencies(
        document=document,
        model_name=ai_config.model_name,
        provider=ai_config.provider,
        temperature=ai_config.temperature,
        api_key=ai_config.api_key
    )
    
    # Create context with the document
    ctx = RunContext(deps)
    
    # Add context to the document
    from datapack.ai.tools import add_context_to_document as add_context_tool
    result = await add_context_tool(
        ctx,
        context=context,
        position=position,
        format_as_comment=format_as_comment
    )
    
    # Update metadata context field if requested
    if track_changes:
        # Get the current context field or initialize it
        metadata_context = document.metadata.get("context", "")
        
        # Get current date in ISO format
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Determine the action description based on result
        action_description = ""
        if result.get("action") == "context_added_to_section":
            action_description = f"Added context to section '{result.get('section', 'unknown')}'"
        elif result.get("action") == "context_added_to_start":
            action_description = "Added context to the start of the document"
        else:
            action_description = "Added context to the end of the document"
        
        # Prepare a snippet of the added content (truncated if too long)
        content_snippet = context
        if len(content_snippet) > 50:
            content_snippet = content_snippet[:47] + "..."
        
        # Format the change entry
        change_entry = f"\n\n[{current_date}] {change_summary or action_description}"
        
        # Append to the context field with content snippet
        if metadata_context:
            document.metadata["context"] = metadata_context + change_entry + f" - {content_snippet}"
        else:
            document.metadata["context"] = f"Document history:\n{change_entry.lstrip()} - {content_snippet}"
        
        result["metadata_updated"] = True
    
    # Save to output path if provided
    if output_path:
        document.save(output_path)
        result["saved_to"] = output_path
    else:
        # Save in place
        document.save()
    
    return result


if __name__ == '__main__':
    sys.exit(main()) 