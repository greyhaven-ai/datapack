"""
Command-line interface for datapack converters.

This module provides CLI commands for converting various data formats to MDP.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from mdp import Document

from datapack.converters import (
    json_to_mdp,
    xml_to_mdp,
    csv_to_mdp,
    yaml_to_mdp,
    markdown_to_mdp,
    api_response_to_mdp,
    sql_to_mdp,
    query_results_to_mdp
)

from .utils import (
    determine_format_type,
    get_output_path,
    parse_metadata,
    parse_key_value_string,
    get_supported_format_types
)

# Conditionally import converters that require additional dependencies
try:
    from datapack.converters import pdf_to_mdp
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from datapack.converters import html_to_mdp
    HTML_SUPPORT = True
except ImportError:
    HTML_SUPPORT = False

try:
    from datapack.converters import docx_to_mdp
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    from datapack.converters import notebook_to_mdp
    NOTEBOOK_SUPPORT = True
except ImportError:
    NOTEBOOK_SUPPORT = False

try:
    from datapack.converters import email_to_mdp
    EMAIL_SUPPORT = True
except ImportError:
    EMAIL_SUPPORT = False

# Check for AI support
AI_SUPPORT = False
try:
    from datapack.ai.models import DocumentMetadata
    from datapack.ai.extractors import MetadataExtractor, ContentStructureExtractor
    AI_SUPPORT = True
except ImportError:
    pass


def convert_file(
    input_path: str,
    output_path: Optional[str] = None,
    format_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    use_ai: bool = False,
    model_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Document:
    """
    Convert a file to MDP format.
    
    Args:
        input_path: Path to the input file
        output_path: Optional path for the output file
        format_type: Type of the input file
        metadata: Optional metadata to include in the MDP document
        use_ai: Whether to use AI for enhanced extraction (if available)
        model_config: Configuration for the AI model if use_ai is True
        **kwargs: Additional format-specific arguments
        
    Returns:
        The converted MDP document
        
    Raises:
        ValueError: If the format type is not supported or cannot be determined
    """
    # Determine format type if not provided
    if not format_type:
        try:
            format_type = determine_format_type(input_path)
        except ValueError as e:
            raise ValueError(f"Could not determine format type: {e}")
    
    # Check if AI enhancement was requested but not available
    if use_ai and not AI_SUPPORT:
        print("Warning: AI enhancement requested but AI support is not available. " 
              "Install with 'pip install datapack[ai]'")
        use_ai = False
    
    # Prepare AI model configuration if needed
    ai_kwargs = {}
    if use_ai and model_config:
        ai_kwargs = {"use_ai": True, "model_config": model_config}
    elif use_ai:
        ai_kwargs = {"use_ai": True}
    
    # Determine output path if not provided
    if not output_path:
        output_path = get_output_path(input_path)
    
    # Convert based on format type
    combined_kwargs = {**kwargs, **ai_kwargs}
    
    if format_type == 'json':
        return json_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'xml':
        return xml_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'csv':
        return csv_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'yaml':
        return yaml_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'markdown':
        return markdown_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'pdf':
        if not PDF_SUPPORT:
            raise ValueError("PDF support is not available. Install with 'pip install datapack[pdf]'")
        return pdf_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'html':
        if not HTML_SUPPORT:
            raise ValueError("HTML support is not available. Install with 'pip install datapack[html]'")
        return html_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'docx':
        if not DOCX_SUPPORT:
            raise ValueError("DOCX support is not available. Install with 'pip install datapack[docx]'")
        return docx_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'notebook':
        if not NOTEBOOK_SUPPORT:
            raise ValueError("Jupyter Notebook support is not available. Install with 'pip install datapack[notebook]'")
        return notebook_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'email':
        if not EMAIL_SUPPORT:
            raise ValueError("Email support is not available. Install with 'pip install datapack[email]'")
        return email_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'sql':
        return sql_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    elif format_type == 'api':
        # This assumes the input_path is a URL or a file containing API responses
        return api_response_to_mdp(input_path, output_path=output_path, metadata=metadata, **combined_kwargs)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")


def parse_model_config(config_str: str) -> Dict[str, Any]:
    """
    Parse AI model configuration from a string.
    
    Args:
        config_str: Configuration string in the format "provider=google,model=gemini-1.5-flash,temperature=0.2"
        
    Returns:
        Dictionary of model configuration
    """
    return parse_key_value_string(config_str)


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """
    Set up the argument parser for the converter CLI.
    
    Args:
        parser: The argument parser to set up
    """
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to the output MDP file (default: input file with .mdp extension)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=get_supported_format_types(),
        help='Format of the input file (default: determined from file extension)'
    )
    parser.add_argument(
        '-m', '--metadata',
        help='Metadata to include in the MDP document (format: key1=value1,key2=value2)'
    )
    
    # AI enhancement options
    parser.add_argument(
        '--use-ai',
        action='store_true',
        help='Use AI to enhance extraction and metadata generation'
    )
    parser.add_argument(
        '--model-config',
        help='AI model configuration (format: provider=google,model=gemini-1.5-flash,temperature=0.2)'
    )
    
    # Format-specific options
    parser.add_argument(
        '--extract-metadata',
        action='store_true',
        help='Extract metadata from the input file if possible'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        help='Maximum number of pages to extract (PDF/DOCX only)'
    )
    parser.add_argument(
        '--include-stats',
        action='store_true',
        help='Include statistics in the output (CSV only)'
    )
    parser.add_argument(
        '--preserve-frontmatter',
        action='store_true',
        help='Preserve frontmatter in the output (Markdown only)'
    )
    parser.add_argument(
        '--include-images',
        action='store_true',
        help='Include images in the output (PDF/HTML/DOCX only)'
    )
    parser.add_argument(
        '--include-code',
        action='store_true',
        help='Include code cells in the output (Notebook only)'
    )
    parser.add_argument(
        '--include-attachments',
        action='store_true',
        help='Include attachments in the output (Email only)'
    )


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the converter CLI.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description='Convert files to MDP format')
    setup_parser(parser)
    
    parsed_args = parser.parse_args(args)
    
    try:
        # Parse metadata
        metadata = parse_metadata(parsed_args.metadata) if parsed_args.metadata else None
        
        # Parse model configuration if AI is used
        model_config = None
        if parsed_args.use_ai and parsed_args.model_config:
            model_config = parse_model_config(parsed_args.model_config)
        
        # Collect format-specific arguments
        kwargs = {}
        if parsed_args.extract_metadata:
            kwargs['extract_metadata'] = True
        if parsed_args.max_pages is not None:
            kwargs['max_pages'] = parsed_args.max_pages
        if parsed_args.include_stats:
            kwargs['include_stats'] = True
        if parsed_args.preserve_frontmatter:
            kwargs['preserve_frontmatter'] = True
        if parsed_args.include_images:
            kwargs['include_images'] = True
        if parsed_args.include_code:
            kwargs['include_code'] = True
        if parsed_args.include_attachments:
            kwargs['include_attachments'] = True
        
        # Convert the file
        doc = convert_file(
            input_path=parsed_args.input,
            output_path=parsed_args.output,
            format_type=parsed_args.format,
            metadata=metadata,
            use_ai=parsed_args.use_ai,
            model_config=model_config,
            **kwargs
        )
        
        print(f"Converted {parsed_args.input} to MDP format")
        print(f"Output file: {parsed_args.output or get_output_path(parsed_args.input)}")
        print(f"Document ID: {doc.id}")
        print(f"Title: {doc.title}")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main()) 