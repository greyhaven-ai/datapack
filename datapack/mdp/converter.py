"""
Document conversion utilities.

This module provides functions for converting various file types to MDP documents.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

from datapack.mdp.document import Document
from datapack.mdp.metadata import create_metadata
from datapack.mdp.utils import convert_to_mdp as _convert_to_mdp
from datapack.mdp.utils import batch_convert_to_mdp as _batch_convert_to_mdp


def convert_file(
    file_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    title: Optional[str] = None,
    add_metadata: Optional[Dict[str, Any]] = None
) -> Document:
    """
    Convert a file to an MDP document.
    
    Args:
        file_path: Path to the file to convert
        output_path: Path to save the converted document (if None, uses the input path with .mdp extension)
        title: Optional title for the document (defaults to filename)
        add_metadata: Additional metadata to include
        
    Returns:
        The converted Document
        
    Raises:
        FileNotFoundError: If the source file does not exist
        ValueError: If the file type is not supported
    """
    file_path = Path(file_path)
    
    # Default output path
    if output_path is None:
        output_path = file_path.with_suffix(".mdp")
    else:
        output_path = Path(output_path)
    
    # Default title
    if title is None:
        title = file_path.stem
    
    # Default metadata
    metadata = {
        "title": title,
        "source_file": file_path.name,
        "source_type": file_path.suffix[1:],  # Remove the dot
    }
    
    # Add additional metadata
    if add_metadata:
        metadata.update(add_metadata)
    
    # Convert using the underlying function
    mdp_file = _convert_to_mdp(
        file_path,
        output_path=output_path,
        metadata=metadata
    )
    
    # Wrap in Document class
    return Document(
        content=mdp_file.content,
        metadata=mdp_file.metadata,
        path=mdp_file.path
    )


def convert_directory(
    directory: Union[str, Path],
    output_directory: Optional[Union[str, Path]] = None,
    recursive: bool = True,
    file_patterns: List[str] = ["*.txt", "*.md", "*.markdown"],
    add_metadata: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """
    Convert all matching files in a directory to MDP documents.
    
    Args:
        directory: The directory containing files to convert
        output_directory: Where to save the converted documents (defaults to input directory)
        recursive: Whether to search subdirectories
        file_patterns: Patterns of files to convert
        add_metadata: Additional metadata to include in all documents
        
    Returns:
        List of converted Document instances
    """
    directory_path = Path(directory)
    
    # Default output directory
    if output_directory is None:
        output_directory = directory_path
    else:
        output_directory = Path(output_directory)
        os.makedirs(output_directory, exist_ok=True)
    
    # Find all files matching the patterns
    files_to_convert = []
    for pattern in file_patterns:
        if recursive:
            files_to_convert.extend(directory_path.glob(f"**/{pattern}"))
        else:
            files_to_convert.extend(directory_path.glob(pattern))
    
    # Convert each file
    converted_docs = []
    for file_path in files_to_convert:
        # Determine the output path
        rel_path = file_path.relative_to(directory_path)
        output_path = output_directory / rel_path.with_suffix(".mdp")
        
        # Create the output directory if needed
        os.makedirs(output_path.parent, exist_ok=True)
        
        try:
            # Convert the file
            doc = convert_file(
                file_path,
                output_path=output_path,
                add_metadata=add_metadata
            )
            converted_docs.append(doc)
        except (ValueError, FileNotFoundError) as e:
            # Skip files that can't be converted but log the error
            print(f"Warning: Could not convert {file_path}: {e}")
    
    return converted_docs


def extract_text_from_pdf(
    pdf_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    title: Optional[str] = None
) -> Document:
    """
    Extract text from a PDF and convert it to an MDP document.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the MDP document (defaults to PDF path with .mdp extension)
        title: Optional title for the document (defaults to PDF filename)
        
    Returns:
        The converted Document
        
    Raises:
        FileNotFoundError: If the PDF file does not exist
        ImportError: If PDF extraction dependencies are not installed
        ValueError: If text extraction fails
    """
    try:
        import pypdf
    except ImportError:
        raise ImportError(
            "PDF extraction requires additional dependencies. "
            "Please install them with: pip install pypdf"
        )
    
    pdf_path = Path(pdf_path)
    
    # Ensure the PDF exists
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Default output path
    if output_path is None:
        output_path = pdf_path.with_suffix(".mdp")
    else:
        output_path = Path(output_path)
    
    # Default title
    if title is None:
        title = pdf_path.stem
    
    # Extract text from PDF
    with open(pdf_path, "rb") as file:
        reader = pypdf.PdfReader(file)
        
        # Get PDF metadata if available
        pdf_info = reader.metadata
        
        # Extract text from all pages
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    
    # Create metadata
    metadata = {
        "title": title,
        "source_file": pdf_path.name,
        "source_type": "pdf",
    }
    
    # Add PDF metadata if available
    if pdf_info:
        if pdf_info.author:
            metadata["author"] = pdf_info.author
        if pdf_info.creation_date:
            metadata["created_at"] = pdf_info.creation_date.strftime("%Y-%m-%d")
    
    # Create the document
    doc = Document(content=text, metadata=metadata)
    
    # Save the document
    doc.save(output_path)
    
    return doc


def import_website(
    url: str,
    output_path: Optional[Union[str, Path]] = None,
    title: Optional[str] = None
) -> Document:
    """
    Import content from a website and convert it to an MDP document.
    
    Args:
        url: The URL to import
        output_path: Path to save the MDP document
        title: Optional title for the document (defaults to page title)
        
    Returns:
        The imported Document
        
    Raises:
        ImportError: If web scraping dependencies are not installed
        ValueError: If the URL is invalid or content extraction fails
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "Web importing requires additional dependencies. "
            "Please install them with: pip install requests beautifulsoup4"
        )
    
    # Default output path
    if output_path is None:
        # Create a filename from the URL's path
        from urllib.parse import urlparse
        url_path = urlparse(url).path
        filename = url_path.strip("/").replace("/", "_") or "index"
        output_path = f"{filename}.mdp"
    
    output_path = Path(output_path)
    
    # Fetch the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    
    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract title
    if title is None:
        title_tag = soup.find("title")
        title = title_tag.text if title_tag else "Imported Web Page"
    
    # Extract content - this is a simple approach; more complex sites may need special handling
    content = ""
    
    # Get main content if available
    main = soup.find("main") or soup.find("article") or soup.find("div", {"id": "content"})
    
    if main:
        # Use the main content area
        content = main.get_text("\n")
    else:
        # Fall back to body content
        body = soup.find("body")
        if body:
            content = body.get_text("\n")
        else:
            content = soup.get_text("\n")
    
    # Clean up the content
    import re
    content = re.sub(r"\n{3,}", "\n\n", content)  # Remove excessive newlines
    
    # Create metadata
    metadata = {
        "title": title,
        "source_url": url,
        "source_type": "web",
    }
    
    # Create the document
    doc = Document(content=content, metadata=metadata)
    
    # Save the document
    doc.save(output_path)
    
    return doc 