"""
Utility functions for datapack CLI.

This module provides shared utility functions for the datapack CLI.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from mdp.metadata import normalize_metadata


def determine_format_type(file_path: str) -> str:
    """
    Determine the format type of a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The format type as a string
        
    Raises:
        ValueError: If the format type cannot be determined
    """
    suffix = Path(file_path).suffix.lower()
    format_map = {
        '.json': 'json',
        '.xml': 'xml',
        '.csv': 'csv',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.pdf': 'pdf',
        '.html': 'html',
        '.htm': 'html',
        '.docx': 'docx',
        '.ipynb': 'notebook',
        '.eml': 'email',
        '.sql': 'sql',
        '.txt': 'text'
    }
    if suffix in format_map:
        return format_map[suffix]
    else:
        raise ValueError(f"Could not determine format type from file extension: {suffix}")


def get_output_path(input_path: str, output_path: Optional[str] = None, extension: str = '.mdp') -> str:
    """
    Determine the output path for a file.
    
    Args:
        input_path: Path to the input file
        output_path: Optional explicit output path
        extension: The extension to use for the output file (default: .mdp)
        
    Returns:
        Path to the output file
    """
    if output_path:
        return output_path
    
    # Use the same name as the input file but with the specified extension
    input_path_obj = Path(input_path)
    return str(input_path_obj.with_suffix(extension))


def parse_key_value_string(kv_str: str, nested_separator: str = '.') -> Dict[str, Any]:
    """
    Parse a key-value string into a dictionary.
    
    Args:
        kv_str: Key-value string in the format "key1=value1,key2=value2"
        nested_separator: Separator for nested keys (default: '.')
        
    Returns:
        Dictionary of parsed key-value pairs
    """
    if not kv_str:
        return {}
    
    result = {}
    pairs = kv_str.split(',')
    
    for pair in pairs:
        if '=' not in pair:
            continue
        
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Handle list values (comma-separated values in brackets)
        if value.startswith('[') and value.endswith(']'):
            value = [item.strip() for item in value[1:-1].split(',')]
        # Handle boolean values
        elif value.lower() in ('true', 'yes'):
            value = True
        elif value.lower() in ('false', 'no'):
            value = False
        # Handle numeric values
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
            value = float(value)
        
        # Handle nested keys
        if nested_separator in key:
            keys = key.split(nested_separator)
            current = result
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        else:
            result[key] = value
    
    return result


def parse_metadata(metadata_str: str) -> Dict[str, Any]:
    """
    Parse metadata from a string and normalize it according to MDP standards.
    
    Args:
        metadata_str: Metadata string in the format "key1=value1,key2=value2"
        
    Returns:
        Dictionary of normalized metadata
    """
    metadata = parse_key_value_string(metadata_str)
    return normalize_metadata(metadata)


def list_files(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    List files in a directory with optional filtering by extension.
    
    Args:
        directory: Directory to list files from
        extensions: Optional list of extensions to filter by (e.g., ['.json', '.csv'])
        
    Returns:
        List of file paths
    """
    files = []
    
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if extensions is None or any(filename.lower().endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return files


def get_supported_format_types() -> List[str]:
    """
    Get a list of supported format types for conversion.
    
    Returns:
        List of supported format types
    """
    return [
        'json',
        'xml',
        'csv',
        'yaml', 
        'markdown',
        'pdf',
        'html',
        'docx',
        'notebook',
        'email',
        'sql',
        'api',
        'text'
    ] 