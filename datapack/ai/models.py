"""
Pydantic models for structured data in datapack.

This module defines the Pydantic models that represent the core data structures
used in datapack, particularly focused on metadata extraction and validation.
"""

from datetime import date as Date
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# AI Configuration Models
class AIModelConfig(BaseModel):
    """Configuration for AI model settings."""
    model_name: str = Field(
        default="gpt-4o",
        description="The name of the AI model to use"
    )
    provider: str = Field(
        default="openai",
        description="The AI provider (e.g., openai, anthropic)"
    )
    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Temperature setting for model responses"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the AI provider"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens for model responses"
    )
    
    @property
    def model_string(self) -> str:
        """Get the full model string in PydanticAI format."""
        return f"{self.provider}:{self.model_name}"

class AISettings(BaseModel):
    """Global AI settings for datapack."""
    default_model: AIModelConfig = Field(
        default_factory=lambda: AIModelConfig(),
        description="Default model configuration"
    )
    metadata_model: Optional[AIModelConfig] = Field(
        default=None,
        description="Model for metadata extraction"
    )
    relationship_model: Optional[AIModelConfig] = Field(
        default=None,
        description="Model for relationship extraction"
    )
    enhancement_model: Optional[AIModelConfig] = Field(
        default=None,
        description="Model for content enhancement"
    )
    pdf_model: Optional[AIModelConfig] = Field(
        default=None,
        description="Model for PDF extraction (preferably multimodal)"
    )
    
    def get_model_config(self, task: str) -> AIModelConfig:
        """Get model configuration for a specific task."""
        if task == "metadata" and self.metadata_model:
            return self.metadata_model
        elif task == "relationship" and self.relationship_model:
            return self.relationship_model
        elif task == "enhancement" and self.enhancement_model:
            return self.enhancement_model
        elif task == "pdf" and self.pdf_model:
            return self.pdf_model
        return self.default_model

class RelationshipType(str, Enum):
    """Valid relationship types between documents."""
    PARENT = "parent"
    CHILD = "child"
    RELATED = "related"
    REFERENCE = "reference"


class Relationship(BaseModel):
    """A relationship between documents."""
    type: RelationshipType
    id: Optional[str] = None
    uri: Optional[str] = None
    path: Optional[str] = None
    cid: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    @field_validator('id')
    def validate_uuid(cls, v):
        """Validate UUID format if present."""
        if v is not None:
            try:
                UUID(v)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v
    
    @field_validator('uri')
    def validate_uri(cls, v):
        """Validate URI format if present."""
        if v is not None and not (v.startswith("mdp://") or v.startswith("ipfs://")):
            raise ValueError(f"Invalid URI: {v}. Must start with 'mdp://' or 'ipfs://'")
        return v
    
    @field_validator('cid')
    def validate_cid(cls, v):
        """Validate IPFS CID format if present."""
        if v is not None:
            # Simple validation for CIDv0 (Qm...) or CIDv1 (b...)
            if not (v.startswith("Qm") and len(v) == 46) and not (v.startswith("b") and len(v) >= 59):
                raise ValueError(f"Invalid IPFS CID format: {v}")
        return v


class CollectionIdType(str, Enum):
    """Valid collection ID types."""
    UUID = "uuid"
    URI = "uri"
    CID = "cid"
    STRING = "string"


class DocumentMetadata(BaseModel):
    """
    The metadata for an MDP document.
    
    This model maps directly to the metadata schema defined in metadata.py.
    """
    # Core fields
    title: str = Field(..., description="The title of the document")
    version: Optional[str] = Field(None, description="The version of the document")
    context: Optional[str] = Field(None, description="Additional context about the document")
    
    # Document identification fields
    uuid: Optional[str] = Field(None, description="Globally unique identifier")
    uri: Optional[str] = Field(None, description="URI reference")
    local_path: Optional[str] = Field(None, description="Local filesystem path relative to a defined root")
    cid: Optional[str] = Field(None, description="IPFS Content Identifier (CID) for content addressing")
    
    # Collection fields
    collection: Optional[str] = Field(None, description="Collection this document belongs to")
    collection_id: Optional[str] = Field(None, description="Unique identifier for the collection")
    collection_id_type: Optional[CollectionIdType] = Field(None, description="Type of identifier used for collection_id")
    position: Optional[int] = Field(None, description="Position in an ordered collection")
    
    # Authorship fields
    author: Optional[str] = Field(None, description="The author of the document")
    contributors: Optional[List[str]] = Field(None, description="List of contributors")
    created_at: Optional[str] = Field(None, description="Creation date (ISO 8601: YYYY-MM-DD)")
    updated_at: Optional[str] = Field(None, description="Last update date (ISO 8601: YYYY-MM-DD)")
    
    # Classification fields
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the document")
    status: Optional[str] = Field(None, description="Status of the document")
    
    # Source fields
    source_file: Optional[str] = Field(None, description="Original file name if converted")
    source_type: Optional[str] = Field(None, description="Original file type if converted")
    source_url: Optional[str] = Field(None, description="URL of the original content")
    source: Optional[Dict[str, Any]] = Field(None, description="Source information including type, conversion details, etc.")
    
    # Relationship fields
    relationships: Optional[List[Relationship]] = Field(None, description="References to related documents")
    
    # Custom fields (with x_ prefix)
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom metadata fields with x_ prefix")
    
    @field_validator('position')
    def validate_position(cls, v):
        """Validate position is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Position must be a non-negative integer")
        return v
    
    @field_validator('created_at', 'updated_at')
    def validate_date_format(cls, v):
        """Validate date format."""
        if v is not None:
            try:
                Date.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Invalid date format: {v}. Expected format: YYYY-MM-DD")
        return v
    
    @field_validator('version')
    def validate_version(cls, v):
        """Validate semantic version format."""
        if v is not None:
            import re
            if not re.match(r'^(\d+)\.(\d+)\.(\d+)$', v):
                raise ValueError(f"Invalid version format: {v}. Expected semantic version (e.g., 1.0.0)")
        return v
    
    @field_validator('cid')
    def validate_cid(cls, v):
        """Validate IPFS CID format."""
        if v is not None:
            # Simple validation for CIDv0 (Qm...) or CIDv1 (b...)
            if not (v.startswith("Qm") and len(v) == 46) and not (v.startswith("b") and len(v) >= 59):
                raise ValueError(f"Invalid IPFS CID format: {v}")
        return v
    
    @field_validator('uri')
    def validate_uri(cls, v):
        """Validate URI format."""
        if v is not None and not (v.startswith("mdp://") or v.startswith("ipfs://")):
            raise ValueError(f"Invalid URI: {v}. Must start with 'mdp://' or 'ipfs://'")
        return v


class ExtractedMetadata(BaseModel):
    """
    Model for metadata extracted from document content.
    
    This represents the output of AI extraction processes and aligns with
    the standard metadata schema defined in metadata.py.
    """
    # Core fields
    title: Optional[str] = Field(None, description="The title of the document")
    version: Optional[str] = Field(None, description="The version of the document")
    context: Optional[str] = Field(None, description="Additional context about the document")
    
    # Document identification fields
    uuid: Optional[str] = Field(None, description="Globally unique identifier")
    uri: Optional[str] = Field(None, description="URI reference")
    local_path: Optional[str] = Field(None, description="Local filesystem path relative to a defined root")
    cid: Optional[str] = Field(None, description="IPFS Content Identifier (CID) for content addressing")
    
    # Collection fields
    collection: Optional[str] = Field(None, description="Collection this document belongs to")
    collection_id: Optional[str] = Field(None, description="Unique identifier for the collection")
    collection_id_type: Optional[CollectionIdType] = Field(None, description="Type of identifier used for collection_id")
    position: Optional[int] = Field(None, description="Position in an ordered collection")
    
    # Authorship fields
    author: Optional[str] = Field(None, description="The author of the document")
    contributors: Optional[List[str]] = Field(None, description="List of contributors")
    created_at: Optional[str] = Field(None, description="Creation date (ISO 8601: YYYY-MM-DD)")
    updated_at: Optional[str] = Field(None, description="Last update date (ISO 8601: YYYY-MM-DD)")
    
    # Classification fields
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the document")
    status: Optional[str] = Field(None, description="Status of the document")
    
    # Source fields
    source_file: Optional[str] = Field(None, description="Original file name if converted")
    source_type: Optional[str] = Field(None, description="Original file type if converted")
    source_url: Optional[str] = Field(None, description="URL of the original content")
    
    # For extraction confidence (not part of standard but useful for AI)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI's confidence in the extraction")


class ContentSection(BaseModel):
    """A section of content extracted from a document."""
    heading: Optional[str] = None
    content: str
    level: Optional[int] = Field(None, ge=1, le=6)
    

class DocumentStructure(BaseModel):
    """
    Structured representation of a document's content.
    
    This model represents the parsed structure of a document,
    used for more advanced document processing.
    """
    sections: List[ContentSection]
    references: Optional[List[str]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    images: Optional[List[str]] = None
    code_blocks: Optional[List[str]] = None 


# PDF-specific models for multimodal extraction
class PDFPageImage(BaseModel):
    """Represents an image on a PDF page."""
    description: str
    relevance: Optional[str] = None
    index: int
    base64_data: Optional[str] = None


class PDFTable(BaseModel):
    """Represents a table extracted from a PDF."""
    headers: Optional[List[str]] = None
    rows: Optional[List[List[str]]] = None
    raw_text: Optional[str] = None
    description: Optional[str] = None


class PDFPageSection(BaseModel):
    """A section within a PDF page."""
    heading: Optional[str] = None
    content: str
    level: Optional[int] = Field(None, ge=1, le=6)


class PDFPage(BaseModel):
    """Structured representation of a PDF page."""
    page_number: int
    content: str
    sections: Optional[List[PDFPageSection]] = None
    images: Optional[List[PDFPageImage]] = None
    tables: Optional[List[PDFTable]] = None
    summary: Optional[str] = None


class PDFDocument(BaseModel):
    """
    Complete structured representation of a PDF document.
    
    This model is designed for multimodal processing of PDF documents,
    including text, images, and tables.
    """
    # Metadata aligned with DocumentMetadata
    metadata: DocumentMetadata
    
    # Content
    pages: List[PDFPage]
    table_of_contents: Optional[List[str]] = None
    overall_summary: Optional[str] = None
    
    # Extraction metadata
    extraction_model: Optional[str] = None
    extraction_timestamp: Optional[str] = None
    multimodal: bool = False 