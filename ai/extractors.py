"""
AI-powered extractors for document metadata and content.

This module provides classes and functions that use PydanticAI to extract
structured information from documents.
"""

from typing import List, Dict, Any, Optional, Union, Type
import re
from pathlib import Path

from pydanticai import PydanticAI
from pydantic import BaseModel

from datapack.ai.models import (
    ExtractedMetadata, 
    DocumentStructure, 
    ContentSection,
    DocumentMetadata
)


class MetadataExtractor:
    """
    Extract metadata from document content using AI.
    
    This class provides methods to extract structured metadata from document content,
    such as titles, tags, and summaries.
    """
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        api_key: Optional[str] = None, 
        temperature: float = 0.0
    ):
        """
        Initialize the metadata extractor.
        
        Args:
            model: The AI model to use for extraction
            api_key: Optional API key for the model provider
            temperature: Temperature setting for generation (lower = more deterministic)
        """
        self.ai = PydanticAI(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract_metadata(
        self, 
        content: str, 
        extract_title: bool = True,
        extract_tags: bool = True,
        extract_summary: bool = True,
        extract_key_points: bool = False,
        extract_entities: bool = False,
        min_confidence: float = 0.7
    ) -> ExtractedMetadata:
        """
        Extract metadata from document content.
        
        Args:
            content: The document content to analyze
            extract_title: Whether to extract a title
            extract_tags: Whether to extract tags
            extract_summary: Whether to extract a summary
            extract_key_points: Whether to extract key points
            extract_entities: Whether to extract entities
            min_confidence: Minimum confidence threshold for extraction
            
        Returns:
            An ExtractedMetadata object with the extracted information
        """
        # Build the system prompt based on requested extractions
        extractions = []
        if extract_title:
            extractions.append("title: A concise, descriptive title that captures the main topic")
        if extract_tags:
            extractions.append("tags: A list of 3-7 relevant keywords or phrases for categorization")
        if extract_summary:
            extractions.append("description: A concise summary (2-3 sentences)")
        if extract_key_points:
            extractions.append("key_points: A list of the 3-5 most important points from the document")
        if extract_entities:
            extractions.append("entities: A list of important named entities (people, organizations, etc.)")
        
        system_prompt = f"""
        You are an expert document analyzer. Extract the following information from the provided document:
        {' '.join(extractions)}
        
        Be accurate and concise. Only extract information that is explicitly present or strongly implied.
        If you're uncertain about any extraction, leave it blank rather than guessing.
        """
        
        user_prompt = f"Document content:\n\n{content[:10000]}"  # Limit to prevent token overflow
        
        # Extract the metadata using PydanticAI
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=ExtractedMetadata
        )
        
        # Filter out low-confidence extractions
        if result.confidence and result.confidence < min_confidence:
            # Reset extractions that might be unreliable
            if extract_tags:
                result.tags = None
            if extract_summary:
                result.summary = None
            if extract_key_points:
                result.key_points = None
        
        return result
    
    def generate_structured_metadata(
        self, 
        content: str,
        filename: Optional[str] = None,
        existing_metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentMetadata:
        """
        Generate a complete metadata structure for an MDP document.
        
        This combines automatic extraction with any existing metadata.
        
        Args:
            content: The document content
            filename: Optional filename for source information
            existing_metadata: Optional existing metadata to augment
            
        Returns:
            A DocumentMetadata object
        """
        # Extract basic metadata first
        extracted = self.extract_metadata(
            content=content,
            extract_title=True,
            extract_tags=True,
            extract_summary=True
        )
        
        # Start building the metadata
        metadata_dict = {}
        
        # Apply existing metadata if provided
        if existing_metadata:
            metadata_dict.update(existing_metadata)
        
        # Apply extracted metadata where not already present
        if extracted.title and "title" not in metadata_dict:
            metadata_dict["title"] = extracted.title
        
        if extracted.tags and "tags" not in metadata_dict:
            metadata_dict["tags"] = extracted.tags
        
        if extracted.description and "description" not in metadata_dict:
            metadata_dict["description"] = extracted.description
        
        # Add source information if filename provided
        if filename and "source_file" not in metadata_dict:
            metadata_dict["source_file"] = filename
            # Try to determine source type from extension
            ext = Path(filename).suffix.lower()
            if ext and "source_type" not in metadata_dict:
                metadata_dict["source_type"] = ext[1:]  # Remove the dot
        
        # Create the DocumentMetadata object
        # If title is missing, use a default
        if "title" not in metadata_dict:
            if filename:
                metadata_dict["title"] = Path(filename).stem
            else:
                metadata_dict["title"] = "Untitled Document"
                
        return DocumentMetadata(**metadata_dict)


class ContentStructureExtractor:
    """
    Extract structured content from documents.
    
    This class provides methods to extract the structure of a document,
    including headings, sections, tables, and other elements.
    """
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        """
        Initialize the content structure extractor.
        
        Args:
            model: The AI model to use for extraction
            api_key: Optional API key for the model provider
            temperature: Temperature setting for generation
        """
        self.ai = PydanticAI(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract_structure(self, content: str) -> DocumentStructure:
        """
        Extract the structure of a document.
        
        Args:
            content: The document content to analyze
            
        Returns:
            A DocumentStructure object representing the document's structure
        """
        system_prompt = """
        You are an expert document structure analyzer. Extract the hierarchical structure 
        of the provided document, including sections, headings, and their content.
        
        For each section, identify:
        1. The heading text (if present)
        2. The heading level (1-6, with 1 being the highest level)
        3. The content of that section
        
        Also identify any references, tables, images, and code blocks present in the document.
        """
        
        user_prompt = f"Document content:\n\n{content[:20000]}"  # Limit to prevent token overflow
        
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=DocumentStructure
        )
        
        return result


class RelationshipExtractor:
    """
    Extract potential document relationships using AI.
    
    This class provides methods to identify potential relationships
    between documents based on their content and metadata.
    """
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        api_key: Optional[str] = None,
        temperature: float = 0.1
    ):
        """
        Initialize the relationship extractor.
        
        Args:
            model: The AI model to use for extraction
            api_key: Optional API key for the model provider
            temperature: Temperature setting for generation
        """
        self.ai = PydanticAI(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract_references(
        self, 
        content: str, 
        document_titles: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract references to other documents.
        
        Args:
            content: The document content to analyze
            document_titles: List of titles of potential reference documents
            
        Returns:
            A list of reference information dictionaries
        """
        # Custom model just for this extraction
        class DocumentReference(BaseModel):
            referenced_title: str
            context: str
            relationship_type: str
            confidence: float
        
        class DocumentReferences(BaseModel):
            references: List[DocumentReference]
        
        system_prompt = f"""
        You are an expert at identifying document references. Analyze the provided document
        and identify any references to documents with the following titles:
        
        {', '.join(document_titles)}
        
        For each reference, extract:
        1. The exact title of the referenced document
        2. The context around the reference
        3. The likely relationship type (parent, child, related, reference)
        4. Your confidence in this reference (0.0-1.0)
        
        Only include definite references, not speculation.
        """
        
        user_prompt = f"Document content:\n\n{content[:15000]}"  # Limit to prevent token overflow
        
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=DocumentReferences
        )
        
        # Filter to higher-confidence references
        high_confidence_refs = [
            {
                "title": ref.referenced_title,
                "context": ref.context,
                "type": ref.relationship_type,
                "confidence": ref.confidence
            }
            for ref in result.references if ref.confidence > 0.7
        ]
        
        return high_confidence_refs 