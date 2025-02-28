"""
AI agents for document processing and enhancement.

This module provides PydanticAI-powered agents for document processing, 
including metadata extraction, content enhancement, and relationship identification.
"""

from typing import List, Dict, Any, Optional, Union, TypeVar, Type
from pathlib import Path
import importlib
import os
import asyncio
from datetime import datetime

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field

from mdp import Document, Collection
from datapack.ai.dependencies import (
    DocumentDependencies, 
    CollectionDependencies,
    DocumentRepositoryDeps,
    FileConversionDeps
)
from datapack.ai.models import (
    Relationship, 
    RelationshipType, 
    AISettings, 
    AIModelConfig
)
from datapack.ai.structured_output import StructuredOutputGenerator

# Global AI settings instance
ai_settings = AISettings()

def configure_ai(settings: Union[AISettings, Dict[str, Any]]) -> None:
    """Configure global AI settings.
    
    Args:
        settings: AISettings instance or dictionary of settings
    """
    global ai_settings
    if isinstance(settings, dict):
        ai_settings = AISettings(**settings)
    else:
        ai_settings = settings

def get_agent_config(task: str) -> AIModelConfig:
    """Get model configuration for a specific task."""
    return ai_settings.get_model_config(task)

class MetadataExtractionResult(BaseModel):
    """Result of metadata extraction aligned with MDP metadata standard."""
    # Core fields
    title: Optional[str] = None
    version: Optional[str] = None
    context: Optional[str] = None
    
    # Document identification fields
    uuid: Optional[str] = None
    uri: Optional[str] = None
    local_path: Optional[str] = None
    cid: Optional[str] = None
    
    # Collection fields
    collection: Optional[str] = None
    collection_id: Optional[str] = None
    collection_id_type: Optional[str] = None
    position: Optional[int] = None
    
    # Authorship fields
    author: Optional[str] = None
    contributors: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Classification fields
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    
    # Source fields
    source_file: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    
    # For extraction confidence (not part of standard but useful for AI)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class RelationshipExtractionResult(BaseModel):
    """Result of relationship extraction."""
    relationships: List[Dict[str, Any]]
    confidence: float = Field(..., ge=0.0, le=1.0)


class SummaryGenerationResult(BaseModel):
    """Result of summary generation."""
    summary: str
    key_points: List[str]
    suggested_title: Optional[str] = None


class DocumentAnalysisResult(BaseModel):
    """Comprehensive result of document analysis."""
    metadata: Dict[str, Any]
    structure: Dict[str, Any]
    insights: List[Dict[str, Any]]
    relationships: Optional[List[Dict[str, Any]]] = None
    suggested_improvements: Optional[List[str]] = None


class ContentEnhancementResult(BaseModel):
    """Result of content enhancement."""
    enhanced_content: str
    changes_made: List[Dict[str, Any]]
    confidence: float = Field(..., ge=0.0, le=1.0)


# Define the document processing agent with configurable model
def create_document_processing_agent() -> Agent:
    """Create a document processing agent with current settings."""
    config = get_agent_config("metadata")
    return Agent(
        config.model_string,
        deps_type=DocumentDependencies,
        result_type=DocumentAnalysisResult,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.api_key,
        system_prompt="""
        You are an expert document analyzer and metadata extractor. Your task is to analyze
        the provided document content and extract comprehensive metadata, identify structure,
        and discover key insights. Be thorough but precise in your analysis.
        """
    )


@document_processing_agent.system_prompt
async def add_document_info(ctx: RunContext[DocumentDependencies]) -> str:
    """Add information about the document to the system prompt."""
    doc = ctx.deps.document
    return f"""
    Document information:
    - Title: {doc.title}
    - Path: {doc.path if doc.path else 'Not saved'}
    - UUID: {doc.metadata.get('uuid', 'None')}
    - Created: {doc.metadata.get('created_at', 'Unknown')}
    - Updated: {doc.metadata.get('updated_at', 'Unknown')}
    """


@document_processing_agent.tool
async def extract_document_structure(
    ctx: RunContext[DocumentDependencies]
) -> Dict[str, Any]:
    """Extract the document's hierarchical structure."""
    from datapack.ai.tools import extract_document_structure
    return await extract_document_structure(ctx)


@document_processing_agent.tool
async def extract_key_insights(
    ctx: RunContext[DocumentDependencies],
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Extract key insights from the document content."""
    from datapack.ai.tools import extract_key_insights
    
    insights = await extract_key_insights(ctx, focus_areas=focus_areas)
    return [insight.dict() for insight in insights]


@document_processing_agent.tool
async def find_document_dependencies(
    ctx: RunContext[DocumentDependencies]
) -> List[Dict[str, Any]]:
    """Find documents that this document depends on or that depend on it."""
    from datapack.ai.tools import find_document_dependencies
    return await find_document_dependencies(ctx)


@document_processing_agent.tool
async def extract_references(
    ctx: RunContext[DocumentDependencies],
    reference_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Extract references from the document content."""
    from datapack.ai.tools import extract_references
    
    references = await extract_references(ctx, reference_types=reference_types)
    return [ref.dict() for ref in references]


# Define the metadata extraction agent with configurable model
def create_metadata_extraction_agent() -> Agent:
    """Create a metadata extraction agent with current settings."""
    config = get_agent_config("metadata")
    return Agent(
        config.model_string,
        deps_type=DocumentDependencies,
        result_type=MetadataExtractionResult,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.api_key,
        system_prompt="""
        You are an expert metadata extractor. Your task is to analyze the provided
        document content and extract essential metadata fields. Focus on accuracy
        and only extract information that is explicitly present or strongly implied.
        """
    )


@metadata_extraction_agent.system_prompt
async def add_extraction_fields(ctx: RunContext[DocumentDependencies]) -> str:
    """Add information about the extraction fields to the system prompt."""
    return """
    Extract the following fields when available in the document, strictly adhering to the MDP metadata standard:
    
    Core fields:
    - title: A concise, descriptive title
    - version: Document version in semantic format (X.Y.Z)
    - context: Background about the document's purpose and audience
    
    Authorship fields:
    - author: The document's creator
    - contributors: List of other contributors
    - created_at: Creation date (YYYY-MM-DD)
    - updated_at: Last update date (YYYY-MM-DD)
    
    Classification fields:
    - tags: Relevant keywords or phrases
    - status: Document status (draft, review, published, etc.)
    
    Source fields (if document was converted):
    - source_file: Original file name if converted
    - source_type: Original file type if converted
    - source_url: URL of original content if applicable
    
    DO NOT extract any fields that are not part of this standard schema.
    Include a confidence score (0.0-1.0) to indicate your confidence in the extraction.
    """


# Define the relationship extraction agent with configurable model
def create_relationship_extraction_agent() -> Agent:
    """Create a relationship extraction agent with current settings."""
    config = get_agent_config("relationship")
    return Agent(
        config.model_string,
        deps_type=DocumentDependencies,
        result_type=RelationshipExtractionResult,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.api_key,
        system_prompt="""
        You are an expert at identifying relationships between documents. Your task
        is to analyze the given document and identify potential relationships with
        other documents that you've been provided information about.
        """
    )


@relationship_extraction_agent.system_prompt
async def add_related_docs_info(ctx: RunContext[DocumentDependencies]) -> str:
    """Add information about related documents to the system prompt."""
    info = "Related documents:\n"
    
    for i, doc in enumerate(ctx.deps.related_documents):
        info += f"{i+1}. {doc.title} (ID: {doc.metadata.get('uuid', 'Unknown')})\n"
        if doc.metadata.get("description"):
            info += f"   Description: {doc.metadata['description'][:100]}...\n"
    
    return info


@relationship_extraction_agent.tool
async def create_document_relationship(
    ctx: RunContext[DocumentDependencies],
    target_document_id: str,
    relationship_type: str = "related",
    description: Optional[str] = None
) -> bool:
    """Create a relationship between the current document and another document."""
    from datapack.ai.tools import create_document_relationship
    return await create_document_relationship(
        ctx,
        target_document_id=target_document_id,
        relationship_type=relationship_type,
        description=description
    )


# Define the summary generation agent
def create_summary_generation_agent() -> Agent:
    """Create a summary generation agent with current settings."""
    config = get_agent_config("enhancement")
    return Agent(
        config.model_string,
        deps_type=DocumentDependencies,
        result_type=SummaryGenerationResult,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.api_key,
        system_prompt="""
        You are an expert document summarizer. Your task is to create a concise yet
        comprehensive summary of the provided document, along with a list of key points.
        Focus on capturing the most important information and main ideas.
        """
    )


# Define the content enhancement agent
def create_content_enhancement_agent() -> Agent:
    """Create a content enhancement agent with current settings."""
    config = get_agent_config("enhancement")
    return Agent(
        config.model_string,
        deps_type=DocumentDependencies,
        result_type=ContentEnhancementResult,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.api_key,
        system_prompt="""
        You are an expert document editor and content enhancer. Your task is to improve
        the provided document by enhancing clarity, fixing errors, improving structure,
        and adding valuable information where appropriate.
        """
    )


@content_enhancement_agent.tool
async def update_document_metadata(
    ctx: RunContext[DocumentDependencies],
    metadata_updates: Dict[str, Any]
) -> Dict[str, Any]:
    """Update metadata fields for the current document."""
    from datapack.ai.tools import update_document_metadata
    return await update_document_metadata(ctx, metadata_updates=metadata_updates)


@content_enhancement_agent.tool
async def update_document_content(
    ctx: RunContext[DocumentDependencies],
    new_content: str,
    section_identifier: Optional[str] = None,
    replace_entire_content: bool = False
) -> Dict[str, Any]:
    """Update the content of the current document."""
    from datapack.ai.tools import update_document_content
    return await update_document_content(
        ctx, 
        new_content=new_content,
        section_identifier=section_identifier,
        replace_entire_content=replace_entire_content
    )


@content_enhancement_agent.tool
async def add_context_to_document(
    ctx: RunContext[DocumentDependencies],
    context: str,
    position: str = "end",
    format_as_comment: bool = False
) -> Dict[str, Any]:
    """Add contextual information to a document without modifying the main content."""
    from datapack.ai.tools import add_context_to_document
    return await add_context_to_document(
        ctx,
        context=context,
        position=position,
        format_as_comment=format_as_comment
    )


@content_enhancement_agent.tool
async def query_document(
    ctx: RunContext[DocumentDependencies],
    query: str,
    section: Optional[str] = None,
    max_context_length: int = 1000
) -> Dict[str, Any]:
    """Query the document for specific information and return relevant context."""
    from datapack.ai.tools import query_document
    return await query_document(
        ctx,
        query=query,
        section=section,
        max_context_length=max_context_length
    )


# Define the file conversion agent
def create_file_conversion_agent() -> Agent:
    """Create a file conversion agent with current settings."""
    config = get_agent_config("metadata")  # Using metadata config as it's most appropriate
    return Agent(
        config.model_string,
        deps_type=DocumentRepositoryDeps,
        result_type=Dict[str, Any],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.api_key,
        system_prompt="""
        You are an expert file converter. Your task is to convert various file formats
        to Markdown Data Pack (MDP) format, extracting and preserving metadata and
        structure as much as possible.
        """
    )


# Define the document collection processing agent
def create_collection_processing_agent() -> Agent:
    """Create a collection processing agent with current settings."""
    config = get_agent_config("metadata")  # Using metadata config as it's most appropriate
    return Agent(
        config.model_string,
        deps_type=CollectionDependencies,
        result_type=Dict[str, Any],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.api_key,
        system_prompt="""
        You are an expert document collection analyzer. Your task is to analyze a
        collection of related documents, identify themes, extract metadata, and
        establish relationships between documents.
        """
    )


@collection_processing_agent.system_prompt
async def add_collection_info(ctx: RunContext[CollectionDependencies]) -> str:
    """Add information about the collection to the system prompt."""
    collection = ctx.deps.collection
    return f"""
    Collection information:
    - Name: {collection.name}
    - Documents: {len(collection.documents)}
    - Collection ID: {collection.metadata.get('collection_id', 'None')}
    """


@collection_processing_agent.tool
async def search_for_documents(
    ctx: RunContext[CollectionDependencies],
    query: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """Search for documents in the collection matching a query."""
    
    results = []
    
    # Simple search implementation
    for doc in ctx.deps.collection.documents:
        # Calculate a basic similarity score based on word overlap
        query_words = set(query.lower().split())
        doc_words = set(doc.content.lower().split())
        if not query_words or not doc_words:
            continue
            
        overlap = len(query_words.intersection(doc_words))
        similarity = overlap / len(query_words) if query_words else 0
        
        if similarity > 0:
            # Get a snippet around the most relevant part
            snippet = None
            if overlap > 0:
                # Find a paragraph containing query terms
                paragraphs = doc.content.split("\n\n")
                for para in paragraphs:
                    if any(word in para.lower() for word in query_words):
                        snippet = para[:200] + "..." if len(para) > 200 else para
                        break
            
            results.append({
                "title": doc.title,
                "document_id": doc.metadata.get("uuid", ""),
                "path": str(doc.path) if doc.path else None,
                "similarity_score": similarity,
                "snippet": snippet
            })
    
    # Sort by similarity and limit results
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:max_results]


class DocumentProcessingAgent:
    """
    High-level agent for document processing that coordinates other agents.
    
    This agent provides a simplified interface for common document processing
    tasks, managing the coordination between specialized agents.
    """
    
    def __init__(
        self, 
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the document processing agent.
        
        Args:
            settings: Optional AI settings to configure the agent
            api_key: Optional API key to override the default
        """
        if settings:
            configure_ai(settings)
        
        if api_key:
            # Update API key in settings
            ai_settings.default_model.api_key = api_key
            
        # Create agent instances with current settings
        self.doc_agent = create_document_processing_agent()
        self.metadata_agent = create_metadata_extraction_agent()
        self.relationship_agent = create_relationship_extraction_agent()
        
        # Initialize the structured output generator
        self.output_generator = StructuredOutputGenerator()

    async def process_document(
        self, 
        document: Union[Document, str, Path],
        extract_metadata: bool = True,
        extract_structure: bool = True,
        extract_relationships: bool = False,
        related_documents: Optional[List[Document]] = None
    ) -> Dict[str, Any]:
        """Process a document with the configured agents."""
        # Convert to Document if path provided
        if isinstance(document, (str, Path)):
            document = Document.from_file(document)
        
        # Create dependencies
        deps = DocumentDependencies(
            document=document,
            related_documents=related_documents or [],
            model_name=self.doc_agent.config.model_string,
            api_key=self.doc_agent.config.api_key,
            temperature=self.doc_agent.config.temperature
        )
        
        # Use the modern agent for processing
        result = await self.doc_agent.run(
            document.content, 
            deps=deps
        )
        
        return result.data
    
    async def extract_metadata(
        self, 
        document: Union[Document, str, Path],
        extract_title: bool = True,
        extract_tags: bool = True,
        extract_summary: bool = True,
        extract_key_points: bool = False,
        extract_entities: bool = False,
        extract_context: bool = False,
        extract_author: bool = False,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """Extract metadata from a document using the configured metadata agent."""
        # Convert to Document if path provided
        if isinstance(document, (str, Path)):
            document = Document.from_file(document)
        
        # Create dependencies
        deps = DocumentDependencies(
            document=document,
            model_name=self.metadata_agent.config.model_string,
            api_key=self.metadata_agent.config.api_key,
            temperature=self.metadata_agent.config.temperature,
            min_confidence=min_confidence
        )
        
        # Use the modern agent for metadata extraction
        result = await self.metadata_agent.run(
            document.content, 
            deps=deps
        )
        
        return result.data.dict()
    
    async def enhance_content(
        self, 
        document: Union[Document, str, Path],
        enhancement_type: str = "general",
        enhancement_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhance document content using the configured enhancement agent."""
        # Convert to Document if path provided
        if isinstance(document, (str, Path)):
            document = Document.from_file(document)
        
        # Create dependencies
        deps = DocumentDependencies(
            document=document,
            model_name=self.doc_agent.config.model_string,
            api_key=self.doc_agent.config.api_key,
            temperature=self.doc_agent.config.temperature
        )
        
        # Use the modern agent for content enhancement
        result = await self.doc_agent.run(
            document.content, 
            deps=deps
        )
        
        # Update the document content
        document.content = result.data.enhanced_content
        
        # Save if document has a path
        if document.path:
            document.save()
        
        return {
            "success": True,
            "changes": result.data.changes_made,
            "confidence": result.data.confidence
        }


class ContentEnhancementAgent:
    """
    Agent class for content enhancement using the modern configuration system.
    """
    
    def __init__(
        self, 
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the content enhancement agent.
        
        Args:
            settings: Optional AI settings to configure the agent
            api_key: Optional API key to override the default
        """
        if settings:
            configure_ai(settings)
        
        if api_key:
            # Update API key in settings
            ai_settings.default_model.api_key = api_key
            
        # Create agent instance with current settings
        self.enhancement_agent = create_content_enhancement_agent()
    
    async def enhance_document(
        self, 
        document: Union[Document, str, Path],
        enhancement_type: str = "general",
        enhancement_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhance a document's content.
        
        Args:
            document: The document to enhance
            enhancement_type: Type of enhancement (general, clarity, expand, summarize)
            enhancement_options: Optional settings for the enhancement
            
        Returns:
            Dictionary with enhancement results
        """
        # Convert to Document if path provided
        if isinstance(document, (str, Path)):
            document = Document.from_file(document)
        
        # Create dependencies
        deps = DocumentDependencies(
            document=document,
            model_name=self.enhancement_agent.config.model_string,
            api_key=self.enhancement_agent.config.api_key,
            temperature=self.enhancement_agent.config.temperature
        )
        
        # Use the agent for content enhancement
        result = await self.enhancement_agent.run(
            f"Enhancement type: {enhancement_type}\n\n{document.content}", 
            deps=deps
        )
        
        # Update the document content
        document.content = result.data.enhanced_content
        
        # Save if document has a path
        if document.path:
            document.save()
        
        return {
            "success": True,
            "changes": result.data.changes_made,
            "confidence": result.data.confidence
        }


class CollectionCreationOutput(BaseModel):
    """Output model for collection creation operations."""
    collection_name: str
    collection_id: str
    parent_document_title: str
    parent_document_id: str
    document_count: int
    document_summaries: List[Dict[str, str]]
    organization_strategy: str


class CollectionCreationAgent:
    """
    Agent for organizing documents into collections and creating parent documents.
    
    This agent processes multiple documents, organizes them into meaningful collections,
    and creates a parent document that serves as a cover page with references to the 
    collection members.
    """
    
    def __init__(
        self, 
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the collection creation agent.
        
        Args:
            settings: Optional AI settings to configure the agent
            api_key: Optional API key to override the default
        """
        if settings:
            configure_ai(settings)
        
        if api_key:
            # Update API key in settings
            ai_settings.default_model.api_key = api_key
            
        # Create agent instances with current settings
        self.collection_agent = create_collection_processing_agent()
        self.metadata_agent = create_metadata_extraction_agent()
        self.doc_agent = create_document_processing_agent()
        
        # Initialize the structured output generator
        self.output_generator = StructuredOutputGenerator()
    
    async def modify_collection(
        self,
        collection: Union[Collection, str, Path],
        action: str,  # "add" or "remove"
        documents: List[Union[Document, str, Path]],
        update_relationships: bool = True,
        update_parent_document: bool = True
    ) -> Dict[str, Any]:
        """
        Modify a collection by adding or removing documents.
        
        Args:
            collection: Collection object or path to collection parent document
            action: "add" or "remove"
            documents: List of documents or document paths to add/remove
            update_relationships: Whether to update relationships between documents
            update_parent_document: Whether to update the parent document
            
        Returns:
            Dict with status and modification results
        """
        # Convert collection to Collection object if needed
        if isinstance(collection, (str, Path)):
            collection_obj = Collection.from_parent_document(collection)
        else:
            collection_obj = collection
        
        # Convert documents to paths
        doc_paths = []
        for doc in documents:
            if isinstance(doc, Document):
                if doc.path:
                    doc_paths.append(str(doc.path))
                else:
                    raise ValueError("Document has no path and cannot be added to collection")
            else:
                doc_paths.append(str(doc))
        
        # Create a context with the collection
        deps = CollectionDependencies(collection=collection_obj)
        ctx = RunContext(deps)
        
        # Use the modify_collection tool
        from datapack.ai.tools import modify_collection
        result = await modify_collection(
            ctx,
            action=action,
            document_paths=doc_paths,
            update_relationships=update_relationships
        )
        
        # Update parent document if requested and we have one
        if update_parent_document and collection_obj.documents and collection_obj.documents[0].metadata.get("is_parent_document"):
            parent_doc = collection_obj.documents[0]
            
            # Update the parent document content to reflect the new collection
            parent_doc = await self._update_parent_document(
                parent_doc,
                collection_obj,
                "organization_by_topic"  # Default organization strategy
            )
            
            # Save the updated parent document
            if parent_doc.path:
                parent_doc.save()
                result["parent_document_updated"] = str(parent_doc.path)
        
        return result
    
    async def _update_parent_document(
        self,
        parent_doc: Document,
        collection: Collection,
        organization_strategy: str
    ) -> Document:
        """
        Update a parent document to reflect changes in the collection.
        
        Args:
            parent_doc: The parent document to update
            collection: The collection containing all documents
            organization_strategy: Strategy for organizing the collection
            
        Returns:
            Updated parent document
        """
        # Extract collection metadata
        collection_name = collection.metadata.get("title", "Document Collection")
        collection_description = collection.metadata.get("description", "A collection of related documents")
        
        # Get child documents (excluding the parent)
        child_docs = [doc for doc in collection.documents if doc.id != parent_doc.id]
        
        # Generate document summaries for the table of contents
        toc_items = []
        for doc in child_docs:
            title = doc.title
            summary = doc.metadata.get("summary", "No summary available")
            doc_id = doc.id
            toc_items.append({
                "title": title,
                "summary": summary,
                "id": doc_id
            })
        
        # Create markdown content for the parent document
        content = f"# {collection_name}\n\n"
        content += f"{collection_description}\n\n"
        content += f"## Collection Overview\n\n"
        content += f"This collection contains {len(child_docs)} documents"
        
        if organization_strategy == "organization_by_topic":
            content += " organized by topic.\n\n"
        elif organization_strategy == "organization_by_date":
            content += " organized chronologically.\n\n"
        else:
            content += ".\n\n"
        
        content += "## Table of Contents\n\n"
        
        for i, item in enumerate(toc_items, 1):
            content += f"{i}. **{item['title']}**"
            if item.get('summary'):
                content += f": {item['summary'][:100]}..."
            content += "\n\n"
        
        # Update the parent document content
        parent_doc.content = content
        
        return parent_doc
            
    async def create_collection_from_documents(
        self,
        documents: List[Union[Document, str, Path]],
        collection_name: str = None,
        base_path: Optional[Path] = None,
        organization_strategy: str = "auto",
        create_parent_document: bool = True,
        extract_relationships: bool = True,
        custom_metadata: Optional[Dict[str, Any]] = None,
        save_documents: bool = True
    ) -> Collection:
        """
        Create a collection from multiple documents.
        
        This function analyzes the documents, groups them into a logical collection,
        establishes relationships between them, and optionally creates a parent
        document that serves as a cover page with references to all documents.
        
        Args:
            documents: List of documents or document paths
            collection_name: Name for the collection (auto-generated if None)
            base_path: Base path to save collection documents
            organization_strategy: How to organize docs ("auto", "thematic", "chronological", "hierarchical")
            create_parent_document: Whether to create a parent document as a cover page
            extract_relationships: Whether to extract relationships between documents
            custom_metadata: Additional metadata for the collection
            save_documents: Whether to save the documents to disk
            
        Returns:
            The created Collection object
        """
        # Convert all documents to Document objects
        doc_objects = []
        for doc in documents:
            if isinstance(doc, (str, Path)):
                doc_objects.append(Document.from_file(doc))
            else:
                doc_objects.append(doc)
        
        # Generate collection name if not provided
        if not collection_name:
            # Extract common themes from documents to generate a collection name
            collection_name = await self._generate_collection_name(doc_objects)
        
        # Create collection with basic metadata
        collection = Collection(
            name=collection_name,
            documents=[],  # We'll add documents after processing
            metadata=custom_metadata
        )
        
        if base_path:
            collection_dir = base_path / collection_name
            os.makedirs(collection_dir, exist_ok=True)
        else:
            # Use directory of first document with a path as the base path
            for doc in doc_objects:
                if doc.path:
                    collection_dir = doc.path.parent / collection_name
                    os.makedirs(collection_dir, exist_ok=True)
                    break
            else:
                # No documents with paths, use current directory
                collection_dir = Path.cwd() / collection_name
                os.makedirs(collection_dir, exist_ok=True)
        
        # Process documents and extract metadata if not already present
        for doc in doc_objects:
            # Extract metadata if not already present
            if not doc.metadata.get("title"):
                metadata = await self._extract_document_metadata(doc)
                for key, value in metadata.items():
                    if value:  # Only add non-empty values
                        doc.metadata[key] = value
            
            # Add to collection
            collection.add_document(doc)
            
            # Save document to collection directory if requested
            if save_documents and collection_dir:
                if not doc.path or doc.path.parent != collection_dir:
                    # Create filename from title
                    safe_title = "".join(c if c.isalnum() else "_" for c in doc.title)
                    doc.save(collection_dir / f"{safe_title}.mdp")
        
        # Extract relationships between documents if requested
        if extract_relationships:
            await self._extract_relationships(collection.documents)
        
        # Create parent document if requested
        if create_parent_document:
            parent_doc = await self._create_parent_document(
                collection, 
                organization_strategy
            )
            # Add parent doc to start of collection
            collection.documents.insert(0, parent_doc)
            
            # Save parent document
            if save_documents and collection_dir:
                parent_doc.save(collection_dir / "cover.mdp")
        
        return collection
    
    async def organize_documents_by_theme(
        self,
        documents: List[Union[Document, str, Path]],
        base_path: Optional[Path] = None,
        max_collections: int = 5,
        min_documents_per_collection: int = 2,
        create_parent_documents: bool = True,
        save_documents: bool = True
    ) -> List[Collection]:
        """
        Organize documents into multiple collections based on themes.
        
        This function analyzes the content of documents and groups them into
        thematic collections based on content similarity.
        
        Args:
            documents: List of documents or document paths
            base_path: Base path to save collection documents
            max_collections: Maximum number of collections to create
            min_documents_per_collection: Minimum documents per collection
            create_parent_documents: Whether to create parent documents for each collection
            save_documents: Whether to save the documents to disk
            
        Returns:
            List of Collection objects
        """
        # Convert all documents to Document objects
        doc_objects = []
        for doc in documents:
            if isinstance(doc, (str, Path)):
                doc_objects.append(Document.from_file(doc))
            else:
                doc_objects.append(doc)
        
        # Use AI to identify themes and group documents
        document_groups = await self._identify_document_themes(
            doc_objects,
            max_collections,
            min_documents_per_collection
        )
        
        # Create a collection for each group
        collections = []
        for theme, docs in document_groups.items():
            # Create a new collection with this theme as name
            collection = await self.create_collection_from_documents(
                documents=docs,
                collection_name=theme,
                base_path=base_path,
                organization_strategy="thematic",
                create_parent_document=create_parent_documents,
                extract_relationships=True,
                save_documents=save_documents
            )
            collections.append(collection)
        
        return collections
    
    async def create_document_collection_by_query(
        self,
        query: str,
        documents: List[Union[Document, str, Path]],
        collection_name: Optional[str] = None,
        base_path: Optional[Path] = None,
        create_parent_document: bool = True,
        save_documents: bool = True,
        max_documents: int = 10
    ) -> Collection:
        """
        Create a collection based on a user query.
        
        This function selects documents that match a query and organizes them
        into a collection.
        
        Args:
            query: The query to match documents against
            documents: List of documents or document paths to search
            collection_name: Name for the collection (generated from query if None)
            base_path: Base path to save collection documents
            create_parent_document: Whether to create a parent document
            save_documents: Whether to save the documents to disk
            max_documents: Maximum number of documents to include
            
        Returns:
            A Collection object containing matching documents
        """
        # Convert all documents to Document objects
        doc_objects = []
        for doc in documents:
            if isinstance(doc, (str, Path)):
                doc_objects.append(Document.from_file(doc))
            else:
                doc_objects.append(doc)
        
        # Generate collection name from query if not provided
        if not collection_name:
            collection_name = f"Collection: {query[:30]}"
            if len(query) > 30:
                collection_name += "..."
        
        # Search for documents matching the query
        matching_docs = await self._search_documents(doc_objects, query, max_documents)
        
        if not matching_docs:
            raise ValueError(f"No documents matched the query: {query}")
        
        # Create a collection with the matching documents
        collection = await self.create_collection_from_documents(
            documents=matching_docs,
            collection_name=collection_name,
            base_path=base_path,
            organization_strategy="query-based",
            create_parent_document=create_parent_document,
            extract_relationships=True,
            custom_metadata={"query": query},
            save_documents=save_documents
        )
        
        return collection
    
    async def _generate_collection_name(self, documents: List[Document]) -> str:
        """Generate a collection name based on document content."""
        # Extract titles and combine first few words from each
        titles = [doc.title for doc in documents if doc.title]
        if not titles:
            return "Document Collection"
        
        # Get common keywords
        words = []
        for title in titles:
            words.extend(title.split()[:2])  # Get first two words of each title
        
        # Count word frequencies
        from collections import Counter
        word_counts = Counter(words)
        
        # Get most common words for the name
        common_words = [word for word, _ in word_counts.most_common(3)]
        
        if common_words:
            return " ".join(common_words) + " Collection"
        else:
            return "Document Collection"
    
    async def _extract_document_metadata(self, document: Document) -> Dict[str, Any]:
        """Extract metadata from a document using AI."""
        deps = DocumentDependencies(
            document=document,
            model_name=self.metadata_agent.config.model_string,
            api_key=self.metadata_agent.config.api_key,
            temperature=self.metadata_agent.config.temperature
        )
        
        # Use the metadata agent to extract metadata
        result = await self.metadata_agent.run(
            document.content, 
            deps=deps
        )
        
        return result.data.dict()
    
    async def _extract_relationships(self, documents: List[Document]) -> None:
        """Extract relationships between documents."""
        # For each document pair, check for relationships
        for i, source_doc in enumerate(documents):
            for j, target_doc in enumerate(documents):
                if i == j:  # Skip self
                    continue
                
                # Check if source document references target document
                if target_doc.title and target_doc.title in source_doc.content:
                    # Create a reference relationship
                    source_doc.add_relationship(
                        target_doc,
                        relationship_type="reference",
                        title=f"Reference to {target_doc.title}"
                    )
    
    async def _create_parent_document(
        self, 
        collection: Collection,
        organization_strategy: str
    ) -> Document:
        """Create a parent document as a cover page for the collection."""
        # Create a document that includes references to all documents in the collection
        title = f"{collection.name} - Overview"
        
        # Start building content
        content = f"# {title}\n\n"
        content += f"This collection contains {len(collection.documents)} documents.\n\n"
        
        # Add collection context
        content += "## Collection Context\n\n"
        content += f"This collection was organized using the '{organization_strategy}' strategy.\n"
        content += f"Collection ID: {collection.metadata.get('collection_id', 'N/A')}\n\n"
        
        # Add document summaries and references
        content += "## Documents in this Collection\n\n"
        
        for i, doc in enumerate(collection.documents):
            # Create a summary of the document
            summary = await self._generate_document_summary(doc)
            
            # Add document reference
            content += f"### {i+1}. {doc.title}\n\n"
            content += f"{summary}\n\n"
            content += f"Document ID: {doc.metadata.get('uuid', 'N/A')}\n\n"
        
        # Create relationships section
        content += "## Document Relationships\n\n"
        
        # Get the collection hierarchy
        hierarchy = collection.get_hierarchy()
        if hierarchy:
            content += "The following relationships exist between documents:\n\n"
            for parent, children in hierarchy.items():
                if children:
                    content += f"- **{parent}** is related to:\n"
                    for child in children:
                        content += f"  - {child}\n"
        else:
            content += "No explicit relationships detected between documents.\n"
        
        # Create the parent document
        parent_doc = Document.create(
            title=title,
            content=content,
            collection=collection.name,
            collection_id=collection.metadata.get("collection_id"),
            collection_id_type="uuid",
            position=0,  # First in the collection
            status="active"
        )
        
        # Make the parent document aware of its children
        for doc in collection.documents:
            parent_doc.add_relationship(
                doc,
                relationship_type="child",
                title=doc.title
            )
        
        return parent_doc
    
    async def _generate_document_summary(self, document: Document) -> str:
        """Generate a brief summary of a document using AI."""
        # Try to use existing description if available
        if document.metadata.get("context"):
            return document.metadata["context"]
        
        # Extract first 1000 characters for summarization
        content_preview = document.content[:1000]
        
        # Create a prompt for the summary
        prompt = f"Please provide a 1-2 sentence summary of the following document excerpt:\n\n{content_preview}..."
        
        # Use the structured output generator to create the summary
        summary_result = await self.output_generator.generate(
            prompt,
            output_type="string",
            model_name=self.metadata_agent.config.model_string,
            temperature=0.3,
            max_tokens=100
        )
        
        return summary_result
    
    async def _identify_document_themes(
        self, 
        documents: List[Document],
        max_themes: int,
        min_docs_per_theme: int
    ) -> Dict[str, List[Document]]:
        """Identify themes in documents and group them."""
        # Extract titles and content previews
        doc_info = []
        for doc in documents:
            doc_info.append({
                "title": doc.title,
                "preview": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
            })
        
        # Create a prompt for theme identification
        prompt = (
            f"Identify up to {max_themes} themes in these documents. "
            f"Each theme should include at least {min_docs_per_theme} documents. "
            f"Format the response as a JSON object with theme names as keys and "
            f"arrays of document indices as values.\n\n"
            f"Documents:\n"
        )
        
        for i, info in enumerate(doc_info):
            prompt += f"{i}. {info['title']}: {info['preview']}\n\n"
        
        # Use the structured output generator to identify themes
        themes_result = await self.output_generator.generate(
            prompt,
            output_type="json",
            model_name=self.doc_agent.config.model_string,
            temperature=0.3
        )
        
        # Convert indices to documents
        document_groups = {}
        for theme, indices in themes_result.items():
            document_groups[theme] = [documents[i] for i in indices if i < len(documents)]
        
        return document_groups
    
    async def _search_documents(
        self, 
        documents: List[Document],
        query: str,
        max_results: int
    ) -> List[Document]:
        """Search for documents matching a query."""
        # Simple search implementation
        results = []
        
        for doc in documents:
            # Calculate a basic similarity score based on word overlap
            query_words = set(query.lower().split())
            doc_words = set((doc.title + " " + doc.content).lower().split())
            
            if not query_words or not doc_words:
                continue
                
            overlap = len(query_words.intersection(doc_words))
            similarity = overlap / len(query_words) if query_words else 0
            
            if similarity > 0:
                results.append((doc, similarity))
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in results[:max_results]]


# Create initial agent instances with default settings
document_processing_agent = create_document_processing_agent()
metadata_extraction_agent = create_metadata_extraction_agent()
relationship_extraction_agent = create_relationship_extraction_agent()
summary_generation_agent = create_summary_generation_agent()
content_enhancement_agent = create_content_enhancement_agent()
file_conversion_agent = create_file_conversion_agent()
collection_processing_agent = create_collection_processing_agent()
collection_creation_agent = CollectionCreationAgent()

# ... rest of the existing code ... 