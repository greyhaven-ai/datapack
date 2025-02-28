"""
AI-powered extractors for document metadata and content.

This module provides classes and functions that use PydanticAI to extract
structured information from documents.
"""

from typing import List, Dict, Any, Optional, Union, Type
import re
import datetime
import base64
from pathlib import Path
import io
import os

from pydanticai import PydanticAI
from pydantic import BaseModel, Field

from datapack.ai.models import (
    ExtractedMetadata, 
    DocumentStructure, 
    ContentSection,
    DocumentMetadata,
    Relationship,
    RelationshipType,
    AISettings,
    AIModelConfig,
    PDFDocument, 
    PDFPage, 
    PDFPageImage, 
    PDFTable,
    PDFPageSection
)
from datapack.ai.prompts import (
    TITLE_EXTRACTION_PROMPT,
    TAG_EXTRACTION_PROMPT,
    SUMMARY_EXTRACTION_PROMPT,
    get_metadata_extraction_prompt
)

# Global settings instance
ai_settings = AISettings()

class MetadataExtractor:
    """
    Extract metadata from document content using AI.
    
    This class provides methods to extract structured metadata from document content,
    such as titles, tags, and summaries.
    """
    
    def __init__(
        self, 
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the metadata extractor.
        
        Args:
            settings: Optional AI settings to configure the extractor
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
    
    def extract_metadata(
        self, 
        content: str, 
        extract_title: bool = True,
        extract_tags: bool = True,
        extract_context: bool = True,
        extract_author: bool = True,
        extract_contributors: bool = False,
        extract_dates: bool = True,
        extract_status: bool = True,
        extract_version: bool = True,
        min_confidence: float = 0.7
    ) -> ExtractedMetadata:
        """
        Extract metadata from document content.
        
        Args:
            content: The document content to analyze
            extract_title: Whether to extract a title
            extract_tags: Whether to extract tags
            extract_context: Whether to extract document context
            extract_author: Whether to extract author information
            extract_contributors: Whether to extract contributor information
            extract_dates: Whether to extract dates (created_at, updated_at)
            extract_status: Whether to extract document status
            extract_version: Whether to extract version information
            min_confidence: Minimum confidence threshold for extraction
            
        Returns:
            An ExtractedMetadata object with the extracted information
        """
        # Get the appropriate system prompt based on requested extractions
        system_prompt = get_metadata_extraction_prompt(
            extract_title=extract_title,
            extract_tags=extract_tags,
            extract_context=extract_context,
            extract_author=extract_author,
            extract_contributors=extract_contributors,
            extract_dates=extract_dates,
            extract_status=extract_status,
            extract_version=extract_version
        )
        
        user_prompt = f"Document content:\n\n{content[:10000]}"  # Limit to prevent token overflow
        
        # Define a Pydantic model for the extraction
        class MetadataExtractionResult(BaseModel):
            title: Optional[str] = None
            tags: Optional[List[str]] = None
            context: Optional[str] = None
            author: Optional[str] = None
            contributors: Optional[List[str]] = None
            created_at: Optional[str] = None
            updated_at: Optional[str] = None
            status: Optional[str] = None
            version: Optional[str] = None
            confidence: float
        
        # Extract the metadata using PydanticAI
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=MetadataExtractionResult
        )
        
        # Filter out low-confidence extractions
        if result.confidence and result.confidence < min_confidence:
            # Reset extractions that might be unreliable
            if extract_tags:
                result.tags = None
            if extract_context:
                result.context = None
            if extract_author:
                result.author = None
            if extract_contributors:
                result.contributors = None
            if extract_status:
                result.status = None
            if extract_version:
                result.version = None
        
        # Convert to ExtractedMetadata
        extracted_metadata = ExtractedMetadata(
            title=result.title,
            tags=result.tags,
            context=result.context,
            author=result.author,
            contributors=result.contributors,
            created_at=result.created_at,
            updated_at=result.updated_at,
            status=result.status,
            version=result.version,
            confidence=result.confidence
        )
        
        return extracted_metadata
    
    def generate_structured_metadata(
        self, 
        content: str,
        filename: Optional[str] = None,
        existing_metadata: Optional[Dict[str, Any]] = None,
        extract_full_metadata: bool = False
    ) -> DocumentMetadata:
        """
        Generate a complete metadata structure for an MDP document.
        
        This combines automatic extraction with any existing metadata.
        
        Args:
            content: The document content
            filename: Optional filename for source information
            existing_metadata: Optional existing metadata to augment
            extract_full_metadata: Whether to extract all possible metadata fields
            
        Returns:
            A DocumentMetadata object
        """
        # Extract metadata with appropriate fields
        extracted = self.extract_metadata(
            content=content,
            extract_title=True,
            extract_tags=True,
            extract_context=True,
            extract_author=True,
            extract_contributors=extract_full_metadata,
            extract_dates=True,
            extract_status=True,
            extract_version=True
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
        
        if extracted.context and "context" not in metadata_dict:
            metadata_dict["context"] = extracted.context
        
        if extracted.author and "author" not in metadata_dict:
            metadata_dict["author"] = extracted.author
        
        if extracted.contributors and "contributors" not in metadata_dict:
            metadata_dict["contributors"] = extracted.contributors
        
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
                "extracted_at": datetime.datetime.now().strftime("%Y-%m-%d"),
                "extractor": "datapack.ai.extractors.MetadataExtractor",
                "model": self.ai.model
            }
        
        # Create the DocumentMetadata object
        # If title is missing, use a default
        if "title" not in metadata_dict:
            if filename:
                metadata_dict["title"] = Path(filename).stem.replace("_", " ").replace("-", " ").title()
            else:
                metadata_dict["title"] = "Untitled Document"
        
        # Ensure created_at is present
        if "created_at" not in metadata_dict:
            metadata_dict["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d")
                
        return DocumentMetadata(**metadata_dict)
    
    def extract_document_relationships(
        self,
        content: str,
        related_documents: List[Dict[str, Any]]
    ) -> List[Relationship]:
        """
        Extract relationships between the current document and other documents.
        
        Args:
            content: The content of the current document
            related_documents: List of dictionaries with 'title' and 'id' keys
            
        Returns:
            A list of Relationship objects
        """
        if not related_documents:
            return []
        
        # Create a system prompt for relationship extraction
        system_prompt = """
        You are an expert at identifying relationships between documents. Your task is to analyze
        the provided document content and determine if it references or relates to any of the
        candidate documents listed.
        
        For each identified relationship, determine:
        1. The type of relationship (parent, child, related, reference)
        2. A brief description of how they are related
        3. Your confidence level (0.0-1.0) that this relationship exists
        
        Only include relationships with a confidence level of 0.7 or higher.
        """
        
        # Create a user prompt with the document content and related document titles
        user_prompt = f"""
        Document content:
        {content[:5000]}
        
        Candidate related documents:
        {', '.join([doc['title'] for doc in related_documents])}
        """
        
        # Define a Pydantic model for the extraction
        class DocumentRelationship(BaseModel):
            related_document_title: str
            relationship_type: str
            description: str
            confidence: float
        
        class RelationshipExtractionResult(BaseModel):
            relationships: List[DocumentRelationship]
        
        # Extract relationships using PydanticAI
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=RelationshipExtractionResult
        )
        
        # Convert to Relationship objects
        relationships = []
        for rel in result.relationships:
            if rel.confidence >= 0.7:
                # Find the document ID for this title
                doc_id = None
                for doc in related_documents:
                    if doc['title'] == rel.related_document_title:
                        doc_id = doc.get('id')
                        break
                
                if doc_id:
                    # Map the relationship type
                    rel_type = RelationshipType.RELATED
                    if rel.relationship_type.lower() == "parent":
                        rel_type = RelationshipType.PARENT
                    elif rel.relationship_type.lower() == "child":
                        rel_type = RelationshipType.CHILD
                    elif rel.relationship_type.lower() == "reference":
                        rel_type = RelationshipType.REFERENCE
                    
                    relationships.append(Relationship(
                        type=rel_type,
                        id=doc_id,
                        title=rel.related_document_title,
                        description=rel.description
                    ))
        
        return relationships


class ContentStructureExtractor:
    """
    Extract structured content from documents.
    
    This class provides methods to extract the structure of a document,
    including headings, sections, tables, and other elements.
    """
    
    def __init__(
        self, 
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the content structure extractor.
        
        Args:
            settings: Optional AI settings to configure the extractor
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
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the relationship extractor.
        
        Args:
            settings: Optional AI settings to configure the extractor
            api_key: Optional API key to override the default
        """
        if settings:
            if isinstance(settings, dict):
                settings = AISettings(**settings)
            global ai_settings
            ai_settings = settings
            
        config = ai_settings.get_model_config("relationship")
        if api_key:
            config.api_key = api_key
            
        self.ai = PydanticAI(
            model=config.model_string,
            api_key=config.api_key,
            temperature=config.temperature
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


class PDFExtractor:
    """
    Extract structured content and metadata from PDF documents using AI.
    
    This class specializes in parsing PDFs, including those with images, complex layouts,
    and hard-to-extract text. It uses multimodal AI models to provide enhanced extraction
    capabilities beyond what traditional PDF parsers can achieve.
    """
    
    def __init__(
        self, 
        settings: Optional[Union[AISettings, Dict[str, Any]]] = None,
        model_name: str = "gemini-1.5-flash",
        provider: str = "google",
        api_key: Optional[str] = None
    ):
        """
        Initialize the PDF extractor.
        
        Args:
            settings: Optional AI settings to configure the extractor
            model_name: Name of the model to use (defaults to gemini-1.5-flash)
            provider: Provider of the model (defaults to google)
            api_key: Optional API key to override the default
        """
        # Use provided settings or global settings
        if settings:
            if isinstance(settings, dict):
                settings = AISettings(**settings)
        else:
            global ai_settings
            settings = ai_settings
            
        # Create model config for PDF extraction
        self.model_config = AIModelConfig(
            model_name=model_name,
            provider=provider,
            temperature=0.0
        )
        
        # If specific API key provided, use it
        if api_key:
            self.model_config.api_key = api_key
            
        # Initialize the PydanticAI client
        self.ai = PydanticAI(
            model=self.model_config.model_string,
            api_key=self.model_config.api_key,
            temperature=self.model_config.temperature
        )
    
    def extract_structured_content(
        self,
        pdf_data: Union[str, Path, bytes, io.BytesIO],
        max_pages: Optional[int] = None,
        include_images: bool = True,
        extract_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Extract structured content from a PDF document.
        
        Args:
            pdf_data: PDF data as a file path, bytes, or BytesIO object
            max_pages: Maximum number of pages to process (None for all)
            include_images: Whether to include images in AI processing
            extract_metadata: Whether to extract metadata
            
        Returns:
            A dictionary containing extracted content and metadata
            
        Raises:
            ImportError: If PDF support is not available
            ValueError: If pdf_data is invalid
        """
        # Ensure PDF support is available
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "PDF support requires additional dependencies. "
                "Install with 'pip install datapack[pdf]' or 'pip install pypdf'"
            )
        
        # Load the PDF
        try:
            if isinstance(pdf_data, (str, Path)):
                pdf_reader = PdfReader(pdf_data)
                filename = str(pdf_data) if isinstance(pdf_data, Path) else pdf_data
            elif isinstance(pdf_data, bytes):
                pdf_reader = PdfReader(io.BytesIO(pdf_data))
                filename = None
            elif isinstance(pdf_data, io.BytesIO):
                pdf_reader = PdfReader(pdf_data)
                filename = None
            else:
                raise ValueError("Invalid PDF data type. Expected file path, bytes, or BytesIO object.")
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {e}") from e
        
        # Determine number of pages to extract
        num_pages = len(pdf_reader.pages)
        pages_to_process = num_pages if max_pages is None else min(max_pages, num_pages)
        
        # Prepare data for AI processing
        pages_data = []
        for i in range(pages_to_process):
            page = pdf_reader.pages[i]
            page_text = page.extract_text() or ""
            
            page_data = {
                "page_number": i + 1,
                "text": page_text,
            }
            
            # Include images if requested
            if include_images:
                image_data = []
                # Extract images from the page
                images = self._extract_page_images(pdf_reader, i)
                
                for j, img_bytes in enumerate(images):
                    try:
                        # Encode image data as base64 for AI processing
                        b64_data = base64.b64encode(img_bytes).decode('utf-8')
                        image_data.append({
                            "image_index": j,
                            "data": b64_data
                        })
                    except Exception:
                        # Skip images that can't be encoded
                        pass
                
                page_data["images"] = image_data
            
            pages_data.append(page_data)
        
        # Process with AI
        import datetime
        
        # Create a schema for AI output that aligns with our models
        class PageImage(BaseModel):
            description: str
            relevance: Optional[str] = None
        
        class TableData(BaseModel):
            headers: Optional[List[str]] = None
            rows: Optional[List[List[str]]] = None
            description: Optional[str] = None
        
        class PageSection(BaseModel):
            heading: Optional[str] = None
            content: str
            level: Optional[int] = Field(None, ge=1, le=6)
        
        class Page(BaseModel):
            page_number: int
            content: str
            sections: Optional[List[PageSection]] = None
            images: Optional[List[PageImage]] = None
            tables: Optional[List[TableData]] = None
            summary: Optional[str] = None
        
        class PDFMetadata(BaseModel):
            title: str
            author: Optional[str] = None
            created_at: Optional[str] = None
            updated_at: Optional[str] = None
            description: Optional[str] = None
            tags: Optional[List[str]] = None
            context: Optional[str] = None
            status: Optional[str] = None
            version: Optional[str] = None
        
        class PDFExtraction(BaseModel):
            metadata: PDFMetadata
            pages: List[Page]
            overall_summary: Optional[str] = None
            table_of_contents: Optional[List[str]] = None
        
        prompt = """
        Extract structured content from this PDF document. Your task is to:
        
        1. Break down the content by pages
        2. For each page, identify headings, text content, tables, and images
        3. Provide a brief summary of each page
        4. Extract complete metadata (title, author, dates, tags, etc.)
        5. Create a coherent overall summary of the document
        6. Generate a table of contents based on the document structure
        
        If the PDF contains images, describe their content and explain their relevance 
        to the surrounding text.
        
        For tables, convert them to a structured format with headers and rows.
        
        Preserve the original document's organization and structure.
        """
        
        # Process the document with AI
        extraction_result = self.ai.generate(PDFExtraction, prompt=prompt, content=pages_data)
        
        # Convert AI output to our internal model format
        # First, process metadata
        metadata_dict = extraction_result.metadata.model_dump(exclude_none=True)
        
        # If filename is available, use it as source_file
        if filename and "source_file" not in metadata_dict:
            metadata_dict["source_file"] = os.path.basename(filename)
            metadata_dict["source_type"] = "pdf"
        
        # Create DocumentMetadata object
        metadata = DocumentMetadata(**metadata_dict)
        
        # Process pages data
        pdf_pages = []
        for page in extraction_result.pages:
            # Process images
            page_images = None
            if page.images:
                page_images = []
                for i, img in enumerate(page.images):
                    page_images.append(PDFPageImage(
                        description=img.description,
                        relevance=img.relevance,
                        index=i,
                        base64_data=None  # We don't store the actual image data in the result
                    ))
            
            # Process tables
            page_tables = None
            if page.tables:
                page_tables = []
                for table in page.tables:
                    page_tables.append(PDFTable(
                        headers=table.headers,
                        rows=table.rows,
                        description=table.description
                    ))
            
            # Process sections
            page_sections = None
            if page.sections:
                page_sections = []
                for section in page.sections:
                    page_sections.append(PDFPageSection(
                        heading=section.heading,
                        content=section.content,
                        level=section.level
                    ))
            
            # Create PDFPage object
            pdf_pages.append(PDFPage(
                page_number=page.page_number,
                content=page.content,
                sections=page_sections,
                images=page_images,
                tables=page_tables,
                summary=page.summary
            ))
        
        # Create the PDFDocument object
        pdf_document = PDFDocument(
            metadata=metadata,
            pages=pdf_pages,
            table_of_contents=extraction_result.table_of_contents,
            overall_summary=extraction_result.overall_summary,
            extraction_model=self.model_config.model_name,
            extraction_timestamp=datetime.datetime.now().isoformat(),
            multimodal=include_images
        )
        
        # Convert to MDP format
        content_sections = []
        
        # Add overall summary if available
        if pdf_document.overall_summary:
            content_sections.append(f"# Summary\n\n{pdf_document.overall_summary}\n")
        
        # Add table of contents if available
        if pdf_document.table_of_contents:
            toc = "# Table of Contents\n\n"
            for item in pdf_document.table_of_contents:
                toc += f"- {item}\n"
            content_sections.append(f"{toc}\n")
        
        # Process each page
        for page in pdf_document.pages:
            page_content = f"## Page {page.page_number}\n\n"
            
            # Add page content
            page_content += page.content
            
            # Add image descriptions if available
            if page.images:
                page_content += "\n\n### Images\n\n"
                for i, image in enumerate(page.images):
                    page_content += f"**Image {i+1}**: {image.description}\n\n"
                    if image.relevance:
                        page_content += f"*Relevance*: {image.relevance}\n\n"
            
            # Add tables if available
            if page.tables:
                page_content += "\n\n### Tables\n\n"
                for i, table in enumerate(page.tables):
                    page_content += f"**Table {i+1}**:\n\n"
                    
                    if table.headers and table.rows:
                        # Create markdown table
                        headers_str = "| " + " | ".join(table.headers) + " |"
                        separator = "| " + " | ".join(["---"] * len(table.headers)) + " |"
                        
                        rows_str = ""
                        for row in table.rows:
                            rows_str += "| " + " | ".join([str(cell) for cell in row]) + " |\n"
                        
                        page_content += f"{headers_str}\n{separator}\n{rows_str}\n"
                    elif table.description:
                        page_content += f"{table.description}\n\n"
            
            # Add page summary if available
            if page.summary:
                page_content += f"\n\n**Summary**: {page.summary}"
            
            content_sections.append(page_content)
        
        # Join all content sections
        content = "\n\n".join(content_sections)
        
        # Prepare metadata for return
        return_metadata = {}
        if extract_metadata:
            # Convert our DocumentMetadata to a dict
            return_metadata = pdf_document.metadata.model_dump(exclude_none=True)
            
            # Add source information
            return_metadata["source"] = {
                "type": "pdf",
                "page_count": num_pages,
                "processed_pages": pages_to_process,
                "processed_with": f"PDFExtractor using {self.model_config.model_name}",
                "processed_at": pdf_document.extraction_timestamp,
                "multimodal": pdf_document.multimodal
            }
        
        return {
            "content": content,
            "metadata": return_metadata,
            "pdf_document": pdf_document  # Return the structured document for advanced usage
        }
    
    def _extract_page_images(self, pdf_reader, page_index: int) -> List[bytes]:
        """
        Extract images from a PDF page.
        
        Args:
            pdf_reader: A PdfReader object
            page_index: The index of the page to extract images from
            
        Returns:
            A list of image data as bytes
        """
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
    
    def _dict_to_markdown_table(self, data: Dict[str, Any]) -> str:
        """
        Convert a dictionary to a markdown table.
        
        Args:
            data: Table data as a dictionary
            
        Returns:
            Markdown formatted table
        """
        if not data:
            return ""
        
        # Handle case where data is a list of dictionaries (rows of data)
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            if not data:
                return ""
            
            # Get all possible headers from all dictionaries
            headers = set()
            for item in data:
                headers.update(item.keys())
            headers = sorted(list(headers))
            
            # Create the header row
            table = "| " + " | ".join(headers) + " |\n"
            # Create the separator row
            table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            # Create data rows
            for item in data:
                row = []
                for header in headers:
                    value = item.get(header, "")
                    row.append(str(value))
                table += "| " + " | ".join(row) + " |\n"
            
            return table
        
        # Handle case where data is a simple dictionary
        headers = data.keys()
        values = [str(val) for val in data.values()]
        
        # Create a simple two-column table
        table = "| Key | Value |\n| --- | --- |\n"
        for key, value in data.items():
            table += f"| {key} | {value} |\n"
        
        return table 