"""
High-level interface for working with MDP documents.

This module provides the Document class, which is the primary interface for working with
Markdown Data Pack (MDP) files in a user-friendly way.
"""

import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterable

from datapack.mdp.core import MDPFile, read_mdp, write_mdp
from datapack.mdp.metadata import (
    create_metadata,
    generate_uuid,
    create_relationship,
    add_relationship_to_metadata,
    DEFAULT_METADATA,
    VALID_RELATIONSHIP_TYPES,
    format_date
)
from datapack.mdp.utils import (
    resolve_reference,
    find_related_documents,
    extract_metadata_from_content
)


class Document:
    """
    A document with metadata and content.
    
    This class provides a high-level interface for working with MDP files,
    abstracting away the low-level details and providing convenient methods
    for common operations.
    
    Attributes:
        content: The markdown content of the document
        metadata: The metadata dictionary of the document
        path: Optional path to the file on disk
    """
    
    def __init__(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        path: Optional[Union[str, Path]] = None
    ):
        """
        Initialize a new Document.
        
        Args:
            content: The markdown content of the document
            metadata: The metadata dictionary (will be validated)
            path: Optional path to the file on disk
        """
        if metadata is None:
            metadata = create_metadata(title="Untitled Document")
        
        self._mdp_file = MDPFile(
            metadata=metadata,
            content=content,
            path=Path(path) if path else None
        )
    
    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Document":
        """
        Create a Document from an MDP file.
        
        Args:
            path: Path to the MDP file
            
        Returns:
            A new Document instance
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid MDP file
        """
        mdp_file = read_mdp(path)
        doc = cls(
            content=mdp_file.content,
            metadata=mdp_file.metadata,
            path=mdp_file.path
        )
        doc._mdp_file = mdp_file  # Store the original MDPFile
        return doc
    
    @classmethod
    def create(
        cls, 
        content: str = "", 
        title: Optional[str] = None, 
        author: Optional[str] = None,
        **metadata_kwargs
    ) -> "Document":
        """
        Create a new Document with sensible defaults.
        
        Args:
            content: The markdown content of the document
            title: The title of the document
            author: The author of the document
            **metadata_kwargs: Additional metadata fields
            
        Returns:
            A new Document instance
        """
        metadata = create_metadata(
            title=title or "Untitled Document",
            author=author,
            **metadata_kwargs
        )
        
        return cls(content=content, metadata=metadata)
    
    @classmethod
    def create_with_auto_metadata(
        cls,
        content: str,
        auto_title: bool = True,
        auto_tags: bool = True,
        auto_summary: bool = True,
        model: Optional[str] = None,
        **metadata_kwargs
    ) -> "Document":
        """
        Create a new Document with automatically extracted metadata.
        
        This method analyzes the content using NLP techniques to automatically
        extract metadata such as title, tags, and summary.
        
        Args:
            content: The markdown content of the document
            auto_title: Whether to automatically extract the title
            auto_tags: Whether to automatically extract tags
            auto_summary: Whether to automatically extract a summary
            model: Optional name of an external model to use for extraction
            **metadata_kwargs: Additional metadata fields (will override extracted ones)
            
        Returns:
            A new Document instance with auto-generated metadata
        """
        # Extract metadata from content
        auto_metadata = extract_metadata_from_content(
            content=content,
            extract_title=auto_title,
            extract_tags=auto_tags,
            extract_summary=auto_summary,
            model=model
        )
        
        # Create base metadata
        metadata = create_metadata(**auto_metadata)
        
        # Override with any explicitly provided metadata
        for key, value in metadata_kwargs.items():
            metadata[key] = value
        
        return cls(content=content, metadata=metadata)
    
    def save(self, path: Optional[Union[str, Path]] = None) -> "Document":
        """
        Save the document to a file.
        
        Args:
            path: The path to save the document to. If None, uses the current path.
            
        Returns:
            The Document instance for method chaining
            
        Raises:
            ValueError: If no path is provided and the document has no path
        """
        if path is not None:
            path = Path(path)
        
        self._mdp_file.save(path)
        return self
    
    def to_string(self) -> str:
        """
        Convert the document to its string representation.
        
        Returns:
            The MDP file format as a string
        """
        return self._mdp_file.to_string()
    
    @property
    def content(self) -> str:
        """Get the document content."""
        return self._mdp_file.content
    
    @content.setter
    def content(self, value: str):
        """Set the document content."""
        self._mdp_file.content = value
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the document metadata."""
        return self._mdp_file.metadata
    
    @property
    def path(self) -> Optional[Path]:
        """Get the document path."""
        return self._mdp_file.path
    
    # Convenience properties for common metadata fields
    
    @property
    def title(self) -> str:
        """Get the document title."""
        return self.metadata.get("title", "")
    
    @title.setter
    def title(self, value: str):
        """Set the document title."""
        self.metadata["title"] = value
    
    @property
    def author(self) -> Optional[str]:
        """Get the document author."""
        return self.metadata.get("author")
    
    @author.setter
    def author(self, value: str):
        """Set the document author."""
        self.metadata["author"] = value
    
    @property
    def created_at(self) -> Optional[str]:
        """Get the document creation date."""
        return self.metadata.get("created_at")
    
    @created_at.setter
    def created_at(self, value: Union[str, date]):
        """Set the document creation date."""
        self.metadata["created_at"] = format_date(value)
    
    @property
    def updated_at(self) -> Optional[str]:
        """Get the document last update date."""
        return self.metadata.get("updated_at")
    
    @updated_at.setter
    def updated_at(self, value: Union[str, date]):
        """Set the document last update date."""
        self.metadata["updated_at"] = format_date(value)
    
    @property
    def tags(self) -> List[str]:
        """Get the document tags."""
        return self.metadata.get("tags", [])
    
    def add_tag(self, tag: str) -> "Document":
        """
        Add a tag to the document.
        
        Args:
            tag: The tag to add
            
        Returns:
            The Document instance for method chaining
        """
        if "tags" not in self.metadata:
            self.metadata["tags"] = []
        
        if tag not in self.metadata["tags"]:
            self.metadata["tags"].append(tag)
        
        return self
    
    def remove_tag(self, tag: str) -> "Document":
        """
        Remove a tag from the document.
        
        Args:
            tag: The tag to remove
            
        Returns:
            The Document instance for method chaining
        """
        if "tags" in self.metadata and tag in self.metadata["tags"]:
            self.metadata["tags"].remove(tag)
        
        return self
    
    # Relationship methods
    
    def add_relationship(
        self,
        target: Union[str, "Document"],
        relationship_type: str = "related",
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> "Document":
        """
        Add a relationship to another document.
        
        Args:
            target: The target document or its identifier (path, UUID, or URI)
            relationship_type: The type of relationship (parent, child, related, reference)
            title: Optional title for the relationship
            description: Optional description of the relationship
            
        Returns:
            The Document instance for method chaining
            
        Raises:
            ValueError: If the relationship type is invalid
        """
        if relationship_type not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(f"Invalid relationship type: {relationship_type}. "
                            f"Must be one of: {', '.join(VALID_RELATIONSHIP_TYPES)}")
        
        # Determine the reference type and value
        if isinstance(target, Document):
            # If the target has a UUID, use that
            if "uuid" in target.metadata:
                ref_id = target.metadata["uuid"]
                is_uri = False
            # If the target has a path, use that
            elif target.path:
                ref_id = str(target.path)
                is_uri = False
            # If all else fails, use the title
            else:
                ref_id = target.title
                is_uri = False
            
            # Use the target's title if none provided
            if title is None:
                title = target.title
        
        # If it's a string, try to determine if it's a path, UUID, or URI
        else:
            ref_id = target
            is_uri = ref_id.startswith("mdp://")
        
        # Convert Path objects to strings if necessary
        if isinstance(ref_id, Path):
            ref_id = str(ref_id)
        
        # Add the relationship to metadata directly with proper parameter forwarding
        add_relationship_to_metadata(
            self.metadata,
            reference=ref_id,
            rel_type=relationship_type,
            title=title,
            description=description,
            is_uri=is_uri
        )
        
        return self
    
    def get_related_documents(
        self,
        relationship_type: Optional[str] = None,
        base_path: Optional[Union[str, Path]] = None
    ) -> List["Document"]:
        """
        Get all related documents of the specified type.
        
        Args:
            relationship_type: Optional type of relationship to filter by
            base_path: Optional base path for resolving relative paths
            
        Returns:
            A list of related Document instances
        """
        # Convert base_path to Path if it's a string
        if base_path is not None and not isinstance(base_path, Path):
            base_path = Path(base_path)
        
        # Use the document's path as the base path if not provided
        if base_path is None and self.path is not None:
            base_path = self.path.parent
        
        # Find the related MDP files
        related_files = find_related_documents(
            self._mdp_file,
            relationship_type=relationship_type,
            base_path=base_path
        )
        
        # Convert them to Document instances
        related_docs = []
        for mdp_file in related_files:
            doc = Document(
                content=mdp_file.content,
                metadata=mdp_file.metadata,
                path=mdp_file.path
            )
            doc._mdp_file = mdp_file  # Store the original MDPFile
            related_docs.append(doc)
        
        return related_docs
    
    def auto_enhance_metadata(
        self,
        update_title: bool = False,
        update_tags: bool = True,
        update_summary: bool = True,
        model: Optional[str] = None
    ) -> "Document":
        """
        Enhance the document's metadata by automatically extracting information from content.
        
        This method analyzes the content using NLP techniques to extract additional
        metadata such as tags and summary. It will not override existing metadata
        unless explicitly told to do so.
        
        Args:
            update_title: Whether to update the title if one is extracted
            update_tags: Whether to update or append tags
            update_summary: Whether to update the description/summary
            model: Optional name of an external model to use for extraction
            
        Returns:
            The Document instance for method chaining
        """
        try:
            # Try to use AI-based extraction if available
            from datapack.ai.extractors import MetadataExtractor
            
            # Create extractor with the specified model or default
            extractor = MetadataExtractor(model=model or "gpt-4o")
            
            # Extract metadata
            extracted = extractor.extract_metadata(
                content=self.content,
                extract_title=update_title,
                extract_tags=update_tags,
                extract_summary=update_summary
            )
            
            # Update metadata selectively
            if update_title and extracted.title:
                self.title = extracted.title
            
            if update_tags and extracted.tags:
                existing_tags = set(self.tags)
                for tag in extracted.tags:
                    if tag not in existing_tags:
                        self.add_tag(tag)
            
            if update_summary and extracted.description:
                self.metadata["description"] = extracted.description
            
            # Add a marker that this was enhanced with AI
            if "x_enhancement" not in self.metadata:
                self.metadata["x_enhancement"] = {}
            
            self.metadata["x_enhancement"]["enhanced_with_ai"] = True
            self.metadata["x_enhancement"]["ai_model"] = model or "gpt-4o"
            self.metadata["x_enhancement"]["enhanced_at"] = format_date(date.today())
            
            return self
            
        except ImportError:
            # Fall back to basic extraction if AI module not available
            # Extract metadata from content using simpler methods
            auto_metadata = extract_metadata_from_content(
                content=self.content,
                extract_title=update_title,
                extract_tags=update_tags,
                extract_summary=update_summary,
                model=model
            )
            
            # Update metadata selectively
            if update_title and "title" in auto_metadata:
                self.title = auto_metadata["title"]
            
            if update_tags and "tags" in auto_metadata:
                existing_tags = set(self.tags)
                for tag in auto_metadata["tags"]:
                    if tag not in existing_tags:
                        self.add_tag(tag)
            
            if update_summary and "description" in auto_metadata:
                self.metadata["description"] = auto_metadata["description"]
            
            return self 