"""
AI-powered document processing workflows.

This module provides complete workflows for processing documents using PydanticAI-powered agents.
These workflows combine multiple agents to provide comprehensive document processing capabilities.
"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import logging

from mdp import Document, Collection
from pydantic_ai import RunContext

from datapack.ai.dependencies import (
    DocumentDependencies,
    CollectionDependencies,
    DocumentRepositoryDeps,
    FileConversionDeps
)
from datapack.ai.agents import (
    document_processing_agent,
    metadata_extraction_agent,
    relationship_extraction_agent,
    content_enhancement_agent,
    collection_processing_agent,
    file_conversion_agent,
    configure_ai,
    ai_settings
)
from datapack.ai.models import AISettings


logger = logging.getLogger(__name__)


async def process_single_document(
    document: Union[Document, str, Path],
    extract_metadata: bool = True,
    extract_insights: bool = True,
    extract_relationships: bool = False,
    enhance_content: bool = False,
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    min_confidence: float = 0.7,
    related_documents: Optional[List[Document]] = None
) -> Document:
    """
    Process a single document using AI agents.
    
    This workflow coordinates multiple AI agents to provide comprehensive document processing:
    - Extract metadata (title, tags, summary, etc.)
    - Extract key insights and structure
    - Identify relationships with other documents
    - Enhance document content
    
    Args:
        document: The document to process (Document instance or path to file)
        extract_metadata: Whether to extract metadata
        extract_insights: Whether to extract key insights
        extract_relationships: Whether to identify relationships with other documents
        enhance_content: Whether to enhance the document content
        settings: Optional AI settings to configure the processing
        api_key: Optional API key to override the default
        min_confidence: Minimum confidence threshold for extractions
        related_documents: List of related documents for relationship extraction
        
    Returns:
        The processed Document instance
    """
    # Configure AI settings if provided
    if settings:
        configure_ai(settings)
    if api_key:
        ai_settings.default_model.api_key = api_key

    # Convert to Document if path provided
    if isinstance(document, (str, Path)):
        document = Document.from_file(document)
    
    # Create basic dependencies
    deps = DocumentDependencies(
        document=document,
        related_documents=related_documents or [],
        min_confidence=min_confidence
    )
    
    # Extract metadata if requested
    if extract_metadata:
        logger.info(f"Extracting metadata for document: {document.title}")
        try:
            metadata_result = await metadata_extraction_agent.run(
                document.content[:10000],  # Limit content for metadata extraction
                deps=deps
            )
            
            # Update document metadata with extracted metadata
            # Only add fields that are in the standard metadata schema
            metadata_dict = metadata_result.data.dict(exclude_none=True, exclude={"confidence"})
            for key, value in metadata_dict.items():
                if value:
                    document.metadata[key] = value
            
            logger.info(f"Metadata extraction completed with confidence: {metadata_result.data.confidence}")
        except Exception as e:
            logger.error(f"Error during metadata extraction: {e}")
    
    # Extract document insights and structure if requested
    if extract_insights:
        logger.info(f"Extracting insights and structure for document: {document.title}")
        try:
            analysis_result = await document_processing_agent.run(
                document.content,
                deps=deps
            )
            
            # Store insights as document metadata
            if "insights" not in document.metadata:
                document.metadata["insights"] = []
            
            document.metadata["insights"].extend(analysis_result.data.insights)
            
            # Store structure as document metadata
            document.metadata["structure"] = analysis_result.data.structure
            
            if analysis_result.data.suggested_improvements:
                document.metadata["suggested_improvements"] = analysis_result.data.suggested_improvements
        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
    
    # Extract relationships if requested and related documents provided
    if extract_relationships and related_documents:
        logger.info(f"Extracting relationships for document: {document.title}")
        try:
            relationship_result = await relationship_extraction_agent.run(
                document.content,
                deps=deps
            )
            
            # Add relationships to document metadata
            if "relationships" not in document.metadata:
                document.metadata["relationships"] = []
            
            document.metadata["relationships"].extend(relationship_result.data.relationships)
            
            logger.info(f"Relationship extraction completed with confidence: {relationship_result.data.confidence}")
        except Exception as e:
            logger.error(f"Error during relationship extraction: {e}")
    
    # Enhance content if requested
    if enhance_content:
        logger.info(f"Enhancing content for document: {document.title}")
        try:
            enhancement_result = await content_enhancement_agent.run(
                document.content,
                deps=deps
            )
            
            # Update document content with enhanced content
            document.content = enhancement_result.data.enhanced_content
            
            # Store enhancement changes in metadata
            document.metadata["enhancement"] = {
                "changes": enhancement_result.data.changes_made,
                "confidence": enhancement_result.data.confidence,
                "timestamp": document.metadata.get("updated_at")
            }
            
            logger.info(f"Content enhancement completed with confidence: {enhancement_result.data.confidence}")
        except Exception as e:
            logger.error(f"Error during content enhancement: {e}")
    
    # Save the document if it has a path
    if document.path:
        document.save()
    
    return document


async def process_collection(
    collection: Collection,
    extract_metadata: bool = True,
    extract_insights: bool = True,
    extract_relationships: bool = True,
    enhance_content: bool = False,
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    min_confidence: float = 0.7,
    max_concurrent: int = 3
) -> Collection:
    """
    Process a collection of documents using AI agents.
    
    This workflow processes all documents in a collection and establishes relationships
    between them.
    
    Args:
        collection: The collection to process
        extract_metadata: Whether to extract metadata for each document
        extract_insights: Whether to extract insights for each document
        extract_relationships: Whether to identify relationships between documents
        enhance_content: Whether to enhance document content
        settings: Optional AI settings to configure the processing
        api_key: Optional API key to override the default
        min_confidence: Minimum confidence threshold for extractions
        max_concurrent: Maximum number of documents to process concurrently
        
    Returns:
        The processed Collection
    """
    # Configure AI settings if provided
    if settings:
        configure_ai(settings)
    if api_key:
        ai_settings.default_model.api_key = api_key

    # Create collection dependencies
    deps = CollectionDependencies(
        collection=collection,
        min_confidence=min_confidence
    )
    
    # Process each document in the collection
    logger.info(f"Processing collection: {collection.name} with {len(collection.documents)} documents")
    
    # Process documents in batches to avoid overwhelming the system
    documents = collection.documents.copy()
    processed_docs = []
    
    for i in range(0, len(documents), max_concurrent):
        batch = documents[i:i+max_concurrent]
        logger.info(f"Processing batch of {len(batch)} documents (batch {i//max_concurrent + 1})")
        
        # Create processing tasks for each document in the batch
        tasks = []
        for doc in batch:
            # If extracting relationships, pass all other documents as related
            related = None
            if extract_relationships:
                related = [d for d in documents if d != doc]
            
            # Create document processing task
            task = process_single_document(
                document=doc,
                extract_metadata=extract_metadata,
                extract_insights=extract_insights,
                extract_relationships=extract_relationships,
                enhance_content=enhance_content,
                min_confidence=min_confidence,
                related_documents=related
            )
            
            tasks.append(task)
        
        # Run all tasks concurrently
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Error processing document {batch[i].title}: {result}")
            else:
                processed_docs.append(result)
    
    # Update collection with processed documents
    collection.documents = processed_docs
    
    # Process the collection as a whole to extract themes and relationships
    logger.info(f"Analyzing collection-level patterns and themes")
    try:
        collection_result = await collection_processing_agent.run(
            f"Collection: {collection.name}\nDocuments: {len(collection.documents)}",
            deps=deps
        )
        
        # Add collection analysis to metadata
        collection.metadata.update(collection_result.data)
        
        logger.info(f"Collection analysis completed")
    except Exception as e:
        logger.error(f"Error during collection analysis: {e}")
    
    return collection


async def convert_and_process_files(
    source_directory: Union[str, Path],
    output_directory: Optional[Union[str, Path]] = None,
    file_pattern: str = "*.*",
    recursive: bool = True,
    create_collection: bool = True,
    extract_metadata: bool = True,
    extract_insights: bool = True,
    extract_relationships: bool = True,
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    min_confidence: float = 0.7,
    max_concurrent: int = 3
) -> Tuple[List[Document], Optional[Collection]]:
    """
    Convert files to MDP format and process them using AI agents.
    
    This workflow:
    1. Finds all matching files in the source directory
    2. Converts them to MDP format
    3. Processes each document with AI agents
    4. Creates a collection if requested
    
    Args:
        source_directory: Directory containing files to convert
        output_directory: Directory to save converted MDP files (defaults to source directory)
        file_pattern: Pattern to match files to convert
        recursive: Whether to recursively process subdirectories
        create_collection: Whether to create a Collection
        extract_metadata: Whether to extract metadata
        extract_insights: Whether to extract insights
        extract_relationships: Whether to identify relationships
        settings: Optional AI settings to configure the processing
        api_key: Optional API key to override the default
        min_confidence: Minimum confidence threshold for extractions
        max_concurrent: Maximum number of documents to process concurrently
        
    Returns:
        A tuple containing a list of processed Documents and an optional Collection
    """
    # Configure AI settings if provided
    if settings:
        configure_ai(settings)
    if api_key:
        ai_settings.default_model.api_key = api_key

    from glob import glob
    import os
    
    # Resolve directories
    source_dir = Path(source_directory)
    output_dir = Path(output_directory) if output_directory else source_dir
    
    # Ensure directories exist
    if not source_dir.exists() or not source_dir.is_dir():
        raise ValueError(f"Invalid source directory: {source_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create repository dependencies
    deps = DocumentRepositoryDeps(
        source_directory=str(source_dir),
        output_directory=str(output_dir),
        min_confidence=min_confidence
    )
    
    # Find all matching files
    pattern = os.path.join(str(source_dir), "**" if recursive else "", file_pattern)
    file_paths = [Path(p) for p in glob(pattern, recursive=recursive)]
    file_paths = [p for p in file_paths if p.is_file()]
    
    logger.info(f"Found {len(file_paths)} files matching pattern '{file_pattern}' in {source_dir}")
    
    # Convert files to MDP format
    documents = []
    for path in file_paths:
        try:
            # Call the file conversion agent
            result = await file_conversion_agent.run(
                f"Convert file: {path.name}",
                deps=deps
            )
            
            # Create a Document from the result
            if result.data and "document_path" in result.data:
                doc_path = Path(result.data["document_path"])
                document = Document.from_file(doc_path)
                documents.append(document)
                logger.info(f"Successfully converted {path} to MDP format")
            else:
                logger.warning(f"Conversion did not return a valid document path for {path}")
        except Exception as e:
            logger.error(f"Error converting {path}: {e}")
    
    # Process the documents
    if documents:
        # Create a collection if requested
        collection = None
        if create_collection and len(documents) > 0:
            collection_name = source_dir.name
            collection = Collection(name=collection_name, documents=documents)
            
            # Process the collection
            collection = await process_collection(
                collection=collection,
                extract_metadata=extract_metadata,
                extract_insights=extract_insights,
                extract_relationships=extract_relationships,
                min_confidence=min_confidence,
                max_concurrent=max_concurrent
            )
            
            # Save the collection
            collection_path = output_dir / f"{collection_name}_collection.json"
            collection.save(collection_path)
            logger.info(f"Saved collection to {collection_path}")
            
            return documents, collection
        else:
            # Process documents individually
            processed_docs = []
            for i in range(0, len(documents), max_concurrent):
                batch = documents[i:i+max_concurrent]
                
                # Create processing tasks
                tasks = []
                for doc in batch:
                    task = process_single_document(
                        document=doc,
                        extract_metadata=extract_metadata,
                        extract_insights=extract_insights,
                        extract_relationships=False,  # No relationships for individual processing
                        min_confidence=min_confidence
                    )
                    tasks.append(task)
                
                # Process batch concurrently
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle results
                for i, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing document {batch[i].title}: {result}")
                    else:
                        processed_docs.append(result)
            
            return processed_docs, None
    
    return documents, None


# Synchronous wrappers for easier usage

def process_document(document, **kwargs):
    """Synchronous wrapper for process_single_document."""
    return asyncio.run(process_single_document(document, **kwargs))


def process_documents(collection, **kwargs):
    """Synchronous wrapper for process_collection."""
    return asyncio.run(process_collection(collection, **kwargs))


def convert_directory(directory, **kwargs):
    """Synchronous wrapper for convert_and_process_files."""
    return asyncio.run(convert_and_process_files(directory, **kwargs)) 