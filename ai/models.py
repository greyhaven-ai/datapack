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
        if v is not None and not v.startswith("mdp://"):
            raise ValueError(f"Invalid MDP URI: {v}. Must start with 'mdp://'")
        return v


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
    local_path: Optional[str] = Field(None, description="Local filesystem path")
    
    # Collection fields
    collection: Optional[str] = Field(None, description="Collection this document belongs to")
    collection_id: Optional[str] = Field(None, description="Unique identifier for the collection")
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
    
    # Relationship fields
    relationships: Optional[List[Relationship]] = Field(None, description="References to related documents")
    
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


class ExtractedMetadata(BaseModel):
    """
    Model for metadata extracted from document content.
    
    This represents the output of AI extraction processes.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    sentiment: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


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