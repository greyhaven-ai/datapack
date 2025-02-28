"""
Structured output generation for document processing.

This module provides functions and classes for generating structured outputs
from document content using PydanticAI, focusing on extracting context and
creating data for MDP metadata fields.
"""

from typing import List, Dict, Any, Optional, Union, Type, TypeVar
from datetime import datetime
from pathlib import Path

from pydanticai import PydanticAI
from pydantic import BaseModel, Field

from datapack.ai.models import (
    DocumentMetadata,
    ExtractedMetadata,
    Relationship,
    RelationshipType,
    AISettings,
    AIModelConfig
)

# Global settings instance
ai_settings = AISettings()

T = TypeVar('T', bound=BaseModel)

class StructuredOutputGenerator:
    """
    Generate structured outputs from document content using PydanticAI.
    
    This class provides methods to extract structured data from documents
    using custom Pydantic models and PydanticAI.
    """
    
    def __init__(
        self,
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the structured output generator.
        
        Args:
            settings: Optional AI settings to configure the generator
            api_key: Optional API key to override the default
        """
        if settings:
            if isinstance(settings, dict):
                settings = AISettings(**settings)
            global ai_settings
            ai_settings = settings
            
        config = ai_settings.get_model_config("metadata")
        if api_key:
            config.api_key = api_key
            
        self.ai = PydanticAI(
            model=config.model_string,
            api_key=config.api_key,
            temperature=config.temperature
        )
    
    def extract_structured_data(
        self,
        content: str,
        output_model: Type[T],
        system_prompt: str,
        user_prompt_prefix: str = "Document content:\n\n"
    ) -> T:
        """
        Extract structured data from document content using a custom Pydantic model.
        
        Args:
            content: The document content to analyze
            output_model: The Pydantic model class to use for structured output
            system_prompt: The system prompt to guide the extraction
            user_prompt_prefix: Optional prefix for the user prompt
            
        Returns:
            An instance of the specified output_model
        """
        # Prepare the user prompt with the document content
        user_prompt = f"{user_prompt_prefix}{content[:10000]}"  # Limit to prevent token overflow
        
        # Extract the structured data using PydanticAI
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=output_model
        )
        
        return result
    
    def extract_document_metadata(
        self,
        content: str,
        filename: Optional[str] = None,
        existing_metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentMetadata:
        """
        Extract comprehensive metadata from document content.
        
        Args:
            content: The document content to analyze
            filename: Optional filename for source information
            existing_metadata: Optional existing metadata to augment
            
        Returns:
            A DocumentMetadata object
        """
        # Define a custom model for metadata extraction
        class ComprehensiveMetadata(BaseModel):
            title: str = Field(..., description="A concise, descriptive title")
            description: str = Field(..., description="A brief summary of the document (2-3 sentences)")
            tags: List[str] = Field(..., description="3-7 relevant keywords or phrases")
            author: Optional[str] = Field(None, description="The document's author or creator")
            created_at: Optional[str] = Field(None, description="Creation date in YYYY-MM-DD format")
            updated_at: Optional[str] = Field(None, description="Last update date in YYYY-MM-DD format")
            status: Optional[str] = Field(None, description="Document status (draft, published, etc.)")
            version: Optional[str] = Field(None, description="Document version in semantic format (e.g., 1.0.0)")
            context: Optional[str] = Field(None, description="Additional context about the document's purpose")
        
        # Create a system prompt for comprehensive metadata extraction
        system_prompt = """
        You are an expert document analyzer. Extract comprehensive metadata from the provided document.
        
        Focus on accuracy and only extract information that is explicitly present or strongly implied.
        If you're uncertain about any field, leave it as null rather than guessing.
        
        For dates, use ISO format (YYYY-MM-DD). If only a month and year are provided, use the first day
        of the month. If only a year is provided, use January 1 of that year.
        
        For version numbers, convert to semantic versioning format (MAJOR.MINOR.PATCH) if possible.
        """
        
        # Extract the metadata
        extracted = self.extract_structured_data(
            content=content,
            output_model=ComprehensiveMetadata,
            system_prompt=system_prompt
        )
        
        # Start building the metadata dictionary
        metadata_dict = {}
        
        # Apply existing metadata if provided
        if existing_metadata:
            metadata_dict.update(existing_metadata)
        
        # Apply extracted metadata where not already present
        if "title" not in metadata_dict:
            metadata_dict["title"] = extracted.title
        
        if "tags" not in metadata_dict:
            metadata_dict["tags"] = extracted.tags
        
        if "context" not in metadata_dict:
            metadata_dict["context"] = extracted.description
        
        # Add additional extracted fields if not already present
        if extracted.author and "author" not in metadata_dict:
            metadata_dict["author"] = extracted.author
        
        if extracted.created_at and "created_at" not in metadata_dict:
            metadata_dict["created_at"] = extracted.created_at
        
        if extracted.updated_at and "updated_at" not in metadata_dict:
            metadata_dict["updated_at"] = extracted.updated_at
        
        if extracted.status and "status" not in metadata_dict:
            metadata_dict["status"] = extracted.status
        
        if extracted.version and "version" not in metadata_dict:
            metadata_dict["version"] = extracted.version
        
        # Add source information if filename provided
        if filename and "source_file" not in metadata_dict:
            metadata_dict["source_file"] = filename
            # Try to determine source type from extension
            ext = Path(filename).suffix.lower()
            if ext and "source_type" not in metadata_dict:
                metadata_dict["source_type"] = ext[1:]  # Remove the dot
        
        # Add source information
        if "source" not in metadata_dict:
            metadata_dict["source"] = {
                "type": "ai_extraction",
                "extracted_at": datetime.now().strftime("%Y-%m-%d"),
                "extractor": "datapack.ai.structured_output.StructuredOutputGenerator",
                "model": self.ai.model
            }
        
        # Ensure created_at is present
        if "created_at" not in metadata_dict:
            metadata_dict["created_at"] = datetime.now().strftime("%Y-%m-%d")
        
        return DocumentMetadata(**metadata_dict)
    
    def extract_document_sections(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract the logical sections of a document.
        
        Args:
            content: The document content to analyze
            
        Returns:
            A list of section dictionaries with heading, content, and level
        """
        # Define a custom model for section extraction
        class DocumentSection(BaseModel):
            heading: Optional[str] = Field(None, description="The section heading or title")
            content: str = Field(..., description="The content of the section")
            level: Optional[int] = Field(None, description="The heading level (1-6)")
        
        class DocumentSections(BaseModel):
            sections: List[DocumentSection] = Field(..., description="The document sections")
        
        # Create a system prompt for section extraction
        system_prompt = """
        You are an expert document analyzer. Extract the logical sections from the provided document.
        
        For each section, identify:
        1. The heading (if present)
        2. The content of that section
        3. The heading level (1 for main headings, 2 for subheadings, etc.)
        
        If a section doesn't have an explicit heading, you can infer one based on the content.
        Ensure that all content from the document is included in at least one section.
        """
        
        # Extract the sections
        result = self.extract_structured_data(
            content=content,
            output_model=DocumentSections,
            system_prompt=system_prompt
        )
        
        # Convert to list of dictionaries
        return [section.model_dump() for section in result.sections]
    
    def extract_document_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extract named entities from document content by category.
        
        Args:
            content: The document content to analyze
            
        Returns:
            A dictionary mapping entity categories to lists of entities
        """
        # Define a custom model for entity extraction
        class DocumentEntities(BaseModel):
            people: List[str] = Field(default_factory=list, description="People mentioned in the document")
            organizations: List[str] = Field(default_factory=list, description="Organizations mentioned in the document")
            locations: List[str] = Field(default_factory=list, description="Locations mentioned in the document")
            products: List[str] = Field(default_factory=list, description="Products mentioned in the document")
            technologies: List[str] = Field(default_factory=list, description="Technologies mentioned in the document")
            concepts: List[str] = Field(default_factory=list, description="Key concepts discussed in the document")
        
        # Create a system prompt for entity extraction
        system_prompt = """
        You are an expert at named entity recognition. Extract important named entities from the
        provided document, categorized by type.
        
        Focus on entities that are central to understanding the document. Only include entities
        that are explicitly mentioned in the text. For each category, list the entities in order
        of importance or frequency of mention.
        
        If a category has no entities, leave it as an empty list.
        """
        
        # Extract the entities
        result = self.extract_structured_data(
            content=content,
            output_model=DocumentEntities,
            system_prompt=system_prompt
        )
        
        # Convert to dictionary
        return result.model_dump()
    
    def extract_document_references(
        self,
        content: str,
        reference_documents: List[Dict[str, str]]
    ) -> List[Relationship]:
        """
        Extract references to other documents.
        
        Args:
            content: The document content to analyze
            reference_documents: List of dictionaries with 'id' and 'title' keys
            
        Returns:
            A list of Relationship objects
        """
        if not reference_documents:
            return []
        
        # Define a custom model for reference extraction
        class DocumentReference(BaseModel):
            document_title: str = Field(..., description="The title of the referenced document")
            relationship_type: str = Field(..., description="The type of relationship")
            description: str = Field(..., description="Description of the relationship")
            confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this reference")
        
        class DocumentReferences(BaseModel):
            references: List[DocumentReference] = Field(..., description="References to other documents")
        
        # Create a system prompt for reference extraction
        titles_str = "\n".join([f"- {doc['title']}" for doc in reference_documents])
        system_prompt = f"""
        You are an expert at identifying references between documents. Analyze the provided document
        and identify any references to the following documents:
        
        {titles_str}
        
        For each reference, determine:
        1. The title of the referenced document
        2. The type of relationship:
           - parent: The referenced document contains or encompasses this document
           - child: The referenced document is contained by or elaborates on this document
           - related: The documents have a non-hierarchical connection
           - reference: The referenced document is cited as an external standard or resource
        3. A brief description of how they are related
        4. Your confidence in this reference (0.0-1.0)
        
        Only include references with a confidence of 0.7 or higher.
        """
        
        # Extract the references
        result = self.extract_structured_data(
            content=content,
            output_model=DocumentReferences,
            system_prompt=system_prompt
        )
        
        # Convert to Relationship objects
        relationships = []
        for ref in result.references:
            if ref.confidence >= 0.7:
                # Find the document ID for this title
                doc_id = None
                for doc in reference_documents:
                    if doc['title'] == ref.document_title:
                        doc_id = doc.get('id')
                        break
                
                if doc_id:
                    # Map the relationship type
                    rel_type = RelationshipType.RELATED
                    if ref.relationship_type.lower() == "parent":
                        rel_type = RelationshipType.PARENT
                    elif ref.relationship_type.lower() == "child":
                        rel_type = RelationshipType.CHILD
                    elif ref.relationship_type.lower() == "reference":
                        rel_type = RelationshipType.REFERENCE
                    
                    relationships.append(Relationship(
                        type=rel_type,
                        id=doc_id,
                        title=ref.document_title,
                        description=ref.description
                    ))
        
        return relationships
    
    def generate_document_summary(
        self,
        content: str,
        length: str = "medium",
        focus: Optional[str] = None
    ) -> str:
        """
        Generate a summary of document content.
        
        Args:
            content: The document content to summarize
            length: The desired summary length ('short', 'medium', or 'long')
            focus: Optional focus area for the summary
            
        Returns:
            A summary of the document
        """
        # Define a custom model for summary generation
        class SummaryResult(BaseModel):
            summary: str = Field(..., description="The document summary")
        
        # Determine the target length based on the length parameter
        target_length = "1-2 paragraphs"
        if length == "short":
            target_length = "2-3 sentences"
        elif length == "long":
            target_length = "3-4 paragraphs"
        
        # Create a system prompt for summary generation
        focus_instruction = ""
        if focus:
            focus_instruction = f" Focus particularly on aspects related to {focus}."
        
        system_prompt = f"""
        You are an expert document summarizer. Create a concise summary of the provided document
        that captures its main purpose, key points, and conclusions.
        
        The summary should be {target_length} in length and written in the third person.{focus_instruction}
        
        Be objective and factual. Include only information that is present in the document.
        """
        
        # Generate the summary
        result = self.extract_structured_data(
            content=content,
            output_model=SummaryResult,
            system_prompt=system_prompt
        )
        
        return result.summary 