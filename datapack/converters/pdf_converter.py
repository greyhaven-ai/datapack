"""
PDF to MDP converter.

This module provides functions to convert PDF data to MDP format,
extracting text content and metadata with optional AI enhancement.
"""

import os
import io
import datetime
import base64
from typing import Dict, Any, Union, Optional, List, Tuple, Callable
from pathlib import Path

try:
    import pypdf
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date
from .utils import normalize_metadata

# Define AI support flag - will be set to True if required packages are installed
AI_SUPPORT = False

# Try to import AI-related dependencies
try:
    from datapack.ai.models import AIModelConfig, AISettings, DocumentMetadata
    from pydanticai import PydanticAI
    AI_SUPPORT = True
except ImportError:
    pass

def _check_pdf_support():
    """
    Check if PDF support is available.
    
    Raises:
        ImportError: If PDF support is not available
    """
    if not PDF_SUPPORT:
        raise ImportError(
            "PDF support requires additional dependencies. "
            "Install with 'pip install datapack[pdf]' or 'pip install pypdf'"
        )

def _check_ai_support():
    """
    Check if AI support is available.
    
    Raises:
        ImportError: If AI support is not available
    """
    if not AI_SUPPORT:
        raise ImportError(
            "AI-powered PDF extraction requires additional dependencies. "
            "Install with 'pip install datapack[ai]' or 'pip install pydanticai'"
        )

def _extract_metadata_from_pdf(pdf_reader: 'PdfReader') -> Dict[str, Any]:
    """
    Extract metadata from a PDF document.
    
    Args:
        pdf_reader: A PdfReader object
        
    Returns:
        A dictionary of metadata
    """
    _check_pdf_support()
    
    metadata = {}
    
    # Extract document info if available
    if pdf_reader.metadata:
        # Map PDF metadata fields to MDP metadata fields
        metadata_mapping = {
            "title": ["/Title"],
            "author": ["/Author", "/Creator"],
            "description": ["/Subject", "/Keywords"],
            "created_at": ["/CreationDate"],
            "updated_at": ["/ModDate"],
            "version": ["/Version"],
        }
        
        for meta_key, pdf_keys in metadata_mapping.items():
            for key in pdf_keys:
                if key in pdf_reader.metadata:
                    value = pdf_reader.metadata[key]
                    # Clean up PDF date format if needed
                    if meta_key in ["created_at", "updated_at"] and value:
                        # PDF dates are often in format: D:YYYYMMDDHHmmSS
                        if isinstance(value, str) and value.startswith("D:"):
                            try:
                                # Extract date components
                                date_str = value[2:]  # Remove D:
                                year = date_str[0:4]
                                month = date_str[4:6]
                                day = date_str[6:8]
                                formatted_date = f"{year}-{month}-{day}"
                                
                                # Add time if available
                                if len(date_str) >= 14:
                                    hour = date_str[8:10]
                                    minute = date_str[10:12]
                                    second = date_str[12:14]
                                    formatted_date += f"T{hour}:{minute}:{second}"
                                
                                value = formatted_date
                            except (ValueError, IndexError):
                                # If parsing fails, keep original value
                                pass
                    
                    metadata[meta_key] = value
                    break
        
        # Add any additional metadata as custom fields
        for key, value in pdf_reader.metadata.items():
            # Skip keys we've already processed
            if any(key in keys for _, keys in metadata_mapping.items()):
                continue
            
            # Add as custom field directly (will be normalized later)
            metadata[key.lstrip('/')] = value
    
    # Add page count
    metadata["page_count"] = len(pdf_reader.pages)
    
    # Normalize metadata to conform to MDP standards
    return normalize_metadata(metadata)

def _extract_text_from_pdf(pdf_reader: 'PdfReader', max_pages: Optional[int] = None) -> str:
    """
    Extract text content from a PDF document.
    
    Args:
        pdf_reader: A PdfReader object
        max_pages: Maximum number of pages to extract (None for all)
        
    Returns:
        Extracted text content
    """
    _check_pdf_support()
    
    content = []
    
    # Determine number of pages to extract
    num_pages = len(pdf_reader.pages)
    pages_to_extract = num_pages if max_pages is None else min(max_pages, num_pages)
    
    # Extract text from each page
    for i in range(pages_to_extract):
        page = pdf_reader.pages[i]
        page_text = page.extract_text()
        
        if page_text:
            content.append(f"## Page {i+1}\n\n{page_text}")
    
    return "\n\n".join(content)

def _get_page_images(pdf_reader: 'PdfReader', page_index: int) -> List[bytes]:
    """
    Extract images from a PDF page.
    
    Args:
        pdf_reader: A PdfReader object
        page_index: The index of the page to extract images from
        
    Returns:
        A list of image data as bytes
    """
    _check_pdf_support()
    
    images = []
    page = pdf_reader.pages[page_index]
    
    if "/Resources" in page and "/XObject" in page["/Resources"]:
        xobject = page["/Resources"]["/XObject"]
        for obj in xobject:
            if xobject[obj]["/Subtype"] == "/Image":
                try:
                    data = xobject[obj].getData()
                    if data:
                        images.append(data)
                except Exception:
                    # Skip images that can't be extracted
                    pass
    
    return images

def _prepare_page_data_for_ai(
    pdf_reader: 'PdfReader', 
    page_index: int, 
    include_images: bool = True
) -> Dict[str, Any]:
    """
    Prepare page data for AI processing.
    
    Args:
        pdf_reader: A PdfReader object
        page_index: The index of the page to prepare
        include_images: Whether to include image data
        
    Returns:
        A dictionary containing page text and optionally image data
    """
    _check_pdf_support()
    
    page = pdf_reader.pages[page_index]
    page_text = page.extract_text() or ""
    
    result = {
        "page_number": page_index + 1,
        "text": page_text,
    }
    
    if include_images:
        image_data = []
        images = _get_page_images(pdf_reader, page_index)
        
        for i, img_bytes in enumerate(images):
            try:
                # Encode image data as base64 for AI processing
                b64_data = base64.b64encode(img_bytes).decode('utf-8')
                image_data.append({
                    "image_index": i,
                    "data": b64_data
                })
            except Exception:
                # Skip images that can't be encoded
                pass
        
        result["images"] = image_data
    
    return result

def _extract_pdf_with_ai(
    pdf_reader: 'PdfReader',
    model_config: Optional[Dict[str, Any]] = None,
    max_pages: Optional[int] = None,
    include_images: bool = True,
    extract_metadata: bool = True
) -> Dict[str, Any]:
    """
    Extract content and metadata from a PDF using AI.
    
    Args:
        pdf_reader: A PdfReader object
        model_config: Configuration for the AI model
        max_pages: Maximum number of pages to process
        include_images: Whether to include images in AI processing
        extract_metadata: Whether to extract metadata
        
    Returns:
        A dictionary containing extracted content and metadata
    """
    _check_pdf_support()
    _check_ai_support()
    
    # Use default model config if none provided
    if model_config is None:
        model_config = {
            "model_name": "gemini-0.0-flash",
            "provider": "google",
            "temperature": 0.0
        }
    
    # Configure the AI model
    model_string = f"{model_config.get('provider', 'google')}:{model_config.get('model_name', 'gemini-1.5-flash')}"
    ai = PydanticAI(
        model=model_string,
        temperature=model_config.get('temperature', 0.0),
        api_key=model_config.get('api_key')
    )
    
    # Determine number of pages to extract
    num_pages = len(pdf_reader.pages)
    pages_to_process = num_pages if max_pages is None else min(max_pages, num_pages)
    
    # Define Pydantic models for structured output
    from pydantic import BaseModel, Field
    
    class PageContent(BaseModel):
        page_number: int
        content: str
        headings: Optional[List[str]] = None
        summary: Optional[str] = None
    
    class PDFContent(BaseModel):
        title: str
        author: Optional[str] = None
        created_at: Optional[str] = None
        updated_at: Optional[str] = None
        description: Optional[str] = None
        tags: Optional[List[str]] = None
        pages: List[PageContent]
        overall_summary: Optional[str] = None
    
    # Prepare data for AI processing
    pages_data = []
    for i in range(pages_to_process):
        page_data = _prepare_page_data_for_ai(pdf_reader, i, include_images)
        pages_data.append(page_data)
    
    # Process with AI
    prompt = """
    Extract structured content from this PDF document. Break down the content by pages,
    identify headings, and provide a brief summary of each page. Also extract metadata 
    like title, author, and create date if present.
    
    If the PDF contains images, describe their content in the relevant page sections.
    
    Use the content structure to maintain the document's organization. Create headings
    that represent the document's structure.
    """
    
    # Process the document with AI
    result = ai.generate(PDFContent, prompt=prompt, content=pages_data)
    
    # Convert AI output to MDP format
    content_sections = []
    for page in result.pages:
        page_content = f"## Page {page.page_number}\n\n"
        
        if page.headings:
            for heading in page.headings:
                page_content += f"### {heading}\n\n"
        
        page_content += page.content
        
        if page.summary:
            page_content += f"\n\n**Summary**: {page.summary}"
        
        content_sections.append(page_content)
    
    content = "\n\n".join(content_sections)
    
    # Extract metadata
    metadata = {}
    if extract_metadata:
        metadata = {
            "title": result.title,
            "author": result.author,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
            "description": result.description or (result.overall_summary if result.overall_summary else None),
            "tags": result.tags,
            "page_count": len(pdf_reader.pages)
        }
        
        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
    
    return {
        "content": content,
        "metadata": metadata
    }

def pdf_to_mdp(
    pdf_data: Union[str, Path, bytes, io.BytesIO], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    max_pages: Optional[int] = None,
    extract_metadata: bool = True,
    use_ai: bool = False,
    model_config: Optional[Dict[str, Any]] = None,
    include_images: bool = True
) -> Document:
    """
    Convert PDF data to an MDP document.
    
    Args:
        pdf_data: PDF data as a file path, bytes, or BytesIO object
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        max_pages: Maximum number of pages to extract (None for all)
        extract_metadata: Whether to extract metadata from the PDF
        use_ai: Whether to use AI for enhanced extraction
        model_config: Configuration for the AI model if use_ai is True
        include_images: Whether to include images in AI processing if use_ai is True
        
    Returns:
        An MDP Document object
        
    Raises:
        ImportError: If PDF support is not available
        ValueError: If pdf_data is invalid
    """
    _check_pdf_support()
    
    # Load the PDF data
    try:
        if isinstance(pdf_data, (str, Path)):
            pdf_reader = PdfReader(pdf_data)
            # Use filename as title if available
            filename = os.path.basename(pdf_data)
            base_name = os.path.splitext(filename)[0]
            default_title = base_name.replace('_', ' ').replace('-', ' ').title()
        elif isinstance(pdf_data, bytes):
            pdf_reader = PdfReader(io.BytesIO(pdf_data))
            default_title = "Converted PDF Document"
        elif isinstance(pdf_data, io.BytesIO):
            pdf_reader = PdfReader(pdf_data)
            default_title = "Converted PDF Document"
        else:
            raise ValueError("Invalid PDF data type. Expected file path, bytes, or BytesIO object.")
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {e}") from e
    
    # Extract content and metadata
    if use_ai:
        try:
            _check_ai_support()
            ai_result = _extract_pdf_with_ai(
                pdf_reader, 
                model_config=model_config,
                max_pages=max_pages,
                include_images=include_images,
                extract_metadata=extract_metadata
            )
            content = ai_result["content"]
            doc_metadata = ai_result["metadata"]
        except ImportError:
            # Fall back to standard extraction if AI support not available
            content = _extract_text_from_pdf(pdf_reader, max_pages)
            doc_metadata = {}
            if extract_metadata:
                doc_metadata = _extract_metadata_from_pdf(pdf_reader)
    else:
        # Standard extraction
        content = _extract_text_from_pdf(pdf_reader, max_pages)
        doc_metadata = {}
        if extract_metadata:
            doc_metadata = _extract_metadata_from_pdf(pdf_reader)
    
    # Override with provided metadata
    if metadata:
        # Normalize the provided metadata too
        normalized_metadata = normalize_metadata(metadata)
        doc_metadata.update(normalized_metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        doc_metadata["title"] = default_title
    
    # Add source information
    source_info = {
        "type": "pdf",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.pdf_converter",
        "page_count": len(pdf_reader.pages)
    }
    
    if use_ai:
        source_info["enhanced_by_ai"] = True
        if model_config and "model_name" in model_config:
            source_info["ai_model"] = model_config["model_name"]
    
    doc_metadata["source"] = source_info
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 