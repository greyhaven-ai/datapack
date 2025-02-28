"""
AI-enhanced document processing for datapack.

This module provides AI-powered capabilities for document processing,
metadata extraction, and content enhancement in datapack.
"""

# Import main classes for easy access
from datapack.ai.models import (
    DocumentMetadata,
    ExtractedMetadata,
    DocumentStructure,
    ContentSection,
    Relationship,
    RelationshipType
)

from datapack.ai.extractors import (
    MetadataExtractor,
    ContentStructureExtractor,
    RelationshipExtractor,
    PDFExtractor
)

from datapack.ai.agents import (
    DocumentProcessingAgent,
    ContentEnhancementAgent
)

from datapack.ai.structured_output import (
    StructuredOutputGenerator
)

__all__ = [
    # Models
    'DocumentMetadata',
    'ExtractedMetadata',
    'DocumentStructure',
    'ContentSection',
    'Relationship',
    'RelationshipType',
    
    # Extractors
    'MetadataExtractor',
    'ContentStructureExtractor',
    'RelationshipExtractor',
    'PDFExtractor',
    
    # Agents
    'DocumentProcessingAgent',
    'ContentEnhancementAgent',
    
    # Structured Output
    'StructuredOutputGenerator',
] 