"""
Datapack: A document ingestion, parsing, and annotation platform.

This package provides tools for working with various document types,
adding metadata, and sharing across software ecosystems.
"""

import typing
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import io

# Direct imports for convenience from the standalone mdp package
from mdp import Document, Collection
import datapack.workflows

# Import converters
import datapack.converters

# Try to import AI capabilities but don't fail if not available
try:
    import datapack.ai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Define version
__version__ = "0.1.0"

# CLI entry point
def cli():
    """Command-line interface entry point."""
    from datapack.cli import main
    main()

# Check if AI capabilities are available
def has_ai_capabilities():
    """Check if AI capabilities are available."""
    return AI_AVAILABLE

# PDF convenience function
def convert_pdf(
    pdf_path: Union[str, Path, bytes, io.BytesIO],
    output_path: Optional[Union[str, Path]] = None,
    use_ai: bool = False,
    model_name: str = "gemini-1.5-flash",
    provider: str = "google",
    api_key: Optional[str] = None,
    max_pages: Optional[int] = None,
    include_images: bool = True,
    extract_metadata: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -> Document:
    """
    Convert a PDF to MDP format with optional AI enhancement.
    
    This is a convenience function that uses the appropriate converter based on
    the use_ai flag. When use_ai is True, it leverages multimodal AI models to
    extract content from PDFs, which is particularly useful for complex PDFs with
    images and formatting.
    
    Args:
        pdf_path: Path to the PDF file, or PDF data as bytes/BytesIO
        output_path: Optional path to save the MDP file
        use_ai: Whether to use AI for enhanced extraction
        model_name: Name of the AI model to use (defaults to gemini-1.5-flash)
        provider: Provider of the AI model (defaults to google)
        api_key: Optional API key for the AI provider
        max_pages: Maximum number of pages to extract (None for all)
        include_images: Whether to include images in AI processing
        extract_metadata: Whether to extract metadata from the PDF
        metadata: Optional metadata to use (overrides extracted metadata)
        
    Returns:
        An MDP Document object
    
    Raises:
        ImportError: If PDF support or AI support is not available
        ValueError: If the PDF is invalid
    
    Examples:
        Basic conversion:
        >>> doc = datapack.convert_pdf("document.pdf", "document.mdp")
        
        AI-enhanced conversion:
        >>> doc = datapack.convert_pdf(
        ...     "complex_document.pdf",
        ...     "enhanced_document.mdp",
        ...     use_ai=True
        ... )
        
        Using a specific model:
        >>> doc = datapack.convert_pdf(
        ...     "document.pdf",
        ...     use_ai=True,
        ...     model_name="custom-model",
        ...     provider="anthropic",
        ...     api_key="your-api-key"
        ... )
    """
    if use_ai and has_ai_capabilities():
        # Use the AI-powered PDF extractor
        pdf_extractor = datapack.ai.PDFExtractor(
            model_name=model_name,
            provider=provider,
            api_key=api_key
        )
        
        # Extract content with AI
        extraction_result = pdf_extractor.extract_structured_content(
            pdf_data=pdf_path,
            max_pages=max_pages,
            include_images=include_images,
            extract_metadata=extract_metadata
        )
        
        # Create document
        content = extraction_result["content"]
        extracted_metadata = extraction_result["metadata"]
        
        # Merge with provided metadata if any
        if metadata:
            extracted_metadata.update(metadata)
        
        doc = Document.create(
            content=content,
            **extracted_metadata
        )
        
        # Save if output path is provided
        if output_path:
            doc.save(output_path)
        
        return doc
    else:
        # Use the standard PDF converter
        model_config = None
        if use_ai:
            model_config = {
                "model_name": model_name,
                "provider": provider,
                "temperature": 0.0,
                "api_key": api_key
            }
        
        # Use the standard converter with optional AI enhancement
        return datapack.converters.pdf_to_mdp(
            pdf_data=pdf_path,
            output_path=output_path,
            metadata=metadata,
            max_pages=max_pages,
            extract_metadata=extract_metadata,
            use_ai=use_ai,
            model_config=model_config,
            include_images=include_images
        )

# What to import with "from datapack import *"
__all__ = [
    "Document",
    "Collection",
    "workflows",
    "converters",
    "has_ai_capabilities",
    "convert_pdf",
]

# Add AI to __all__ if available
if AI_AVAILABLE:
    __all__.append("ai")
