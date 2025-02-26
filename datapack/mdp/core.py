"""
Core functionality for working with MDP (Markdown Data Pack) files.

This module provides the main MDPFile class and functions for reading and writing .mdp files.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from datapack.mdp.metadata import extract_metadata, validate_metadata


@dataclass
class MDPFile:
    """
    Represents an MDP (Markdown Data Pack) file with metadata and content.
    
    An MDP file is a text file with YAML frontmatter metadata at the top,
    followed by markdown content. The metadata is separated from the content
    by a line with three dashes (---).
    
    Attributes:
        metadata: A dictionary containing the metadata from the YAML frontmatter
        content: The markdown content of the file
        path: Optional path to the file on disk
    """
    
    metadata: Dict[str, Any]
    content: str
    path: Optional[Path] = None
    
    def __post_init__(self) -> None:
        """Validate metadata after initialization."""
        validate_metadata(self.metadata)
    
    def to_string(self) -> str:
        """
        Convert the MDP file to a string representation.
        
        Returns:
            A string representation of the MDP file with YAML frontmatter and content.
        """
        yaml_str = yaml.dump(self.metadata, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_str}---\n\n{self.content}"
    
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Save the MDP file to disk.
        
        Args:
            path: The path to save the file to. If None, uses the path attribute.
        
        Raises:
            ValueError: If no path is provided and the path attribute is None.
        """
        if path is None:
            if self.path is None:
                raise ValueError("No path provided to save the MDP file.")
            save_path = self.path
        else:
            save_path = Path(path)
        
        # Ensure the directory exists
        os.makedirs(save_path.parent, exist_ok=True)
        
        # Write the file
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(self.to_string())
        
        # Update the path attribute
        self.path = save_path


def read_mdp(path: Union[str, Path]) -> MDPFile:
    """
    Read an MDP file from disk.
    
    Args:
        path: The path to the MDP file.
    
    Returns:
        An MDPFile object representing the file.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid MDP file.
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"MDP file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    metadata, markdown_content = extract_metadata(content)
    
    return MDPFile(
        metadata=metadata,
        content=markdown_content,
        path=file_path
    )


def write_mdp(
    path: Union[str, Path],
    metadata: Dict[str, Any],
    content: str
) -> MDPFile:
    """
    Write an MDP file to disk.
    
    Args:
        path: The path to write the MDP file to.
        metadata: The metadata to include in the YAML frontmatter.
        content: The markdown content of the file.
    
    Returns:
        An MDPFile object representing the file.
    
    Raises:
        ValueError: If the metadata is not valid.
    """
    mdp_file = MDPFile(metadata=metadata, content=content, path=Path(path))
    mdp_file.save()
    return mdp_file 