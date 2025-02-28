"""
Dependency injection system for AI document processing.

This module provides dependency containers and context managers for AI-powered
document processing, making it easy to provide document repositories, file systems,
and other services to AI agents.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union, Type
from pathlib import Path

from mdp import Document, Collection
from datapack.ai.models import AIModelConfig, AISettings

# Global settings instance
ai_settings = AISettings()

@dataclass
class DocumentDependencies:
    """
    Dependencies for document processing operations.
    
    This container provides access to a single document and its related
    context for AI processing operations.
    """
    document: Document
    base_path: Optional[Path] = None
    related_documents: List[Document] = field(default_factory=list)
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.0
    min_confidence: float = 0.7
    
    def __post_init__(self):
        # Ensure the document is saved if we need to access related documents
        if self.base_path is None and self.document.path is not None:
            self.base_path = self.document.path.parent
            
        # Use default model settings if not provided
        if self.model_name is None:
            config = ai_settings.default_model
            self.model_name = config.model_string
            self.api_key = config.api_key
            self.temperature = config.temperature


@dataclass
class CollectionDependencies:
    """
    Dependencies for collection processing operations.
    
    This container provides access to a document collection and its
    context for AI processing operations.
    """
    collection: Collection
    base_path: Optional[Path] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.0
    min_confidence: float = 0.7
    
    def __post_init__(self):
        # Set base path if not provided
        if self.base_path is None and self.collection.documents:
            for doc in self.collection.documents:
                if doc.path is not None:
                    self.base_path = doc.path.parent
                    break
                    
        # Use default model settings if not provided
        if self.model_name is None:
            config = ai_settings.default_model
            self.model_name = config.model_string
            self.api_key = config.api_key
            self.temperature = config.temperature


@dataclass
class DocumentRepositoryDeps:
    """
    Dependencies for document repository operations.
    
    This container provides access to a repository of documents and
    operations for searching, retrieving, and managing documents.
    """
    base_directory: Path
    documents: Dict[str, Document] = field(default_factory=dict)
    collections: Dict[str, Collection] = field(default_factory=dict)
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    
    def __post_init__(self):
        # Create the directory if it doesn't exist
        self.base_directory.mkdir(parents=True, exist_ok=True)
        
        # Use default model settings if not provided
        if self.model_name is None:
            config = ai_settings.default_model
            self.model_name = config.model_string
            self.api_key = config.api_key

    def load_document(self, path: Union[str, Path]) -> Document:
        """Load a document from the repository."""
        path_str = str(path)
        if path_str not in self.documents:
            full_path = self.base_directory / path
            self.documents[path_str] = Document.from_file(full_path)
        return self.documents[path_str]
    
    def save_document(self, document: Document, path: Optional[Union[str, Path]] = None) -> Path:
        """Save a document to the repository."""
        if path is not None:
            save_path = self.base_directory / path
        elif document.path is not None:
            save_path = document.path
        else:
            # Create a filename based on the title
            safe_title = "".join(c if c.isalnum() else "_" for c in document.title)
            save_path = self.base_directory / f"{safe_title}.mdp"
        
        document.save(save_path)
        self.documents[str(save_path.relative_to(self.base_directory))] = document
        return save_path
    
    def load_collection(self, name: str) -> Collection:
        """Load a collection from the repository."""
        if name not in self.collections:
            collection_dir = self.base_directory / name
            if not collection_dir.exists():
                raise ValueError(f"Collection directory not found: {collection_dir}")
            self.collections[name] = Collection.from_directory(collection_dir, name=name)
        return self.collections[name]
    
    def find_related_documents(self, document: Document) -> List[Document]:
        """Find documents related to the given document."""
        related_docs = []
        for doc_path, doc in self.documents.items():
            # Skip the document itself
            if doc.path == document.path:
                continue
            
            # Check if the document title appears in this document's content
            if document.title and document.title in doc.content:
                related_docs.append(doc)
            
            # Check relationships
            if "relationships" in doc.metadata:
                for rel in doc.metadata["relationships"]:
                    if "uuid" in document.metadata and rel.get("id") == document.metadata["uuid"]:
                        related_docs.append(doc)
                    elif document.path and rel.get("path") == str(document.path):
                        related_docs.append(doc)
        
        return related_docs


@dataclass
class FileConversionDeps:
    """
    Dependencies for file conversion operations.
    
    This container provides context for converting files to MDP format,
    including source and destination paths.
    """
    source_directory: Path
    output_directory: Path
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    
    def __post_init__(self):
        # Create directories if they don't exist
        self.source_directory.mkdir(parents=True, exist_ok=True)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Use default model settings if not provided
        if self.model_name is None:
            config = ai_settings.default_model
            self.model_name = config.model_string
            self.api_key = config.api_key 