"""
AI agents for document processing in datapack.

This module provides higher-level AI agents that coordinate multiple
extractors and provide complete document processing capabilities.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import os

from datapack.mdp.document import Document
from datapack.mdp.collection import Collection
from datapack.mdp.metadata import create_metadata

from datapack.ai.extractors import (
    MetadataExtractor,
    ContentStructureExtractor,
    RelationshipExtractor
)
from datapack.ai.models import DocumentMetadata


class DocumentProcessingAgent:
    """
    High-level agent for comprehensive document processing.
    
    This agent coordinates multiple specialized extractors to process
    documents, extract metadata, analyze structure, identify relationships,
    and create richly annotated MDP documents.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        metadata_temperature: float = 0.0,
        structure_temperature: float = 0.0,
        relationship_temperature: float = 0.1
    ):
        """
        Initialize the document processing agent.
        
        Args:
            model: The AI model to use for all extractors
            api_key: Optional API key for the model provider
            metadata_temperature: Temperature for metadata extraction
            structure_temperature: Temperature for structure extraction
            relationship_temperature: Temperature for relationship extraction
        """
        # Initialize the specialized extractors
        self.metadata_extractor = MetadataExtractor(
            model=model, 
            api_key=api_key,
            temperature=metadata_temperature
        )
        
        self.structure_extractor = ContentStructureExtractor(
            model=model,
            api_key=api_key,
            temperature=structure_temperature
        )
        
        self.relationship_extractor = RelationshipExtractor(
            model=model,
            api_key=api_key,
            temperature=relationship_temperature
        )
    
    def process_document(
        self,
        content: str,
        filename: Optional[str] = None,
        existing_metadata: Optional[Dict[str, Any]] = None,
        extract_structure: bool = False,
        related_documents: Optional[List[Document]] = None
    ) -> Document:
        """
        Process a document and create an MDP Document.
        
        Args:
            content: The document content to process
            filename: Optional filename for source information
            existing_metadata: Optional existing metadata to include
            extract_structure: Whether to extract document structure
            related_documents: Optional list of potentially related documents
            
        Returns:
            A Document instance with extracted metadata
        """
        # Extract metadata
        metadata_obj = self.metadata_extractor.generate_structured_metadata(
            content=content,
            filename=filename,
            existing_metadata=existing_metadata
        )
        
        # Convert Pydantic model to dict for Document creation
        metadata_dict = metadata_obj.model_dump(exclude_none=True)
        
        # Extract relationships if related documents provided
        if related_documents and len(related_documents) > 0:
            # Get titles of related documents
            titles = [doc.title for doc in related_documents if doc.title]
            
            # Extract references
            references = self.relationship_extractor.extract_references(
                content=content,
                document_titles=titles
            )
            
            # Add relationships to metadata
            for ref in references:
                # Find the referenced document
                for doc in related_documents:
                    if doc.title == ref["title"]:
                        # Add relationship
                        if "relationships" not in metadata_dict:
                            metadata_dict["relationships"] = []
                        
                        # Create relationship entry
                        relationship = {
                            "type": ref["type"],
                            "title": ref["title"]
                        }
                        
                        # Use UUID if available, otherwise path
                        if "uuid" in doc.metadata:
                            relationship["id"] = doc.metadata["uuid"]
                        elif doc.path:
                            relationship["path"] = str(doc.path)
                        
                        # Add description from context
                        if "context" in ref and ref["context"]:
                            relationship["description"] = f"Referenced in context: '{ref['context']}'"
                        
                        metadata_dict["relationships"].append(relationship)
        
        # Create the Document
        document = Document(
            content=content,
            metadata=metadata_dict
        )
        
        return document
    
    def process_file(
        self,
        file_path: Union[str, Path],
        extract_structure: bool = False,
        related_documents: Optional[List[Document]] = None
    ) -> Document:
        """
        Process a file and create an MDP Document.
        
        Args:
            file_path: Path to the file to process
            extract_structure: Whether to extract document structure
            related_documents: Optional list of potentially related documents
            
        Returns:
            A Document instance with extracted metadata
            
        Raises:
            FileNotFoundError: If the file does not exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Read the file content
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Process the document
        document = self.process_document(
            content=content,
            filename=path.name,
            extract_structure=extract_structure,
            related_documents=related_documents
        )
        
        # Set the document path
        document._mdp_file.path = path
        
        return document
    
    def process_directory(
        self,
        directory_path: Union[str, Path],
        recursive: bool = True,
        file_pattern: str = "*.*",
        create_collection: bool = True,
        analyze_relationships: bool = True
    ) -> Tuple[List[Document], Optional[Collection]]:
        """
        Process all files in a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to recursively process subdirectories
            file_pattern: Pattern to match files to process
            create_collection: Whether to create a Collection
            analyze_relationships: Whether to analyze relationships between documents
            
        Returns:
            A tuple containing a list of processed Documents and an optional Collection
        """
        from glob import glob
        import os
        
        dir_path = Path(directory_path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid directory: {dir_path}")
        
        # Find all matching files
        pattern = os.path.join(str(dir_path), "**" if recursive else "", file_pattern)
        file_paths = [Path(p) for p in glob(pattern, recursive=recursive)]
        
        # Process each file individually
        documents = []
        for path in file_paths:
            if path.is_file():
                try:
                    doc = self.process_file(path)
                    documents.append(doc)
                except Exception as e:
                    print(f"Error processing {path}: {e}")
        
        # Analyze relationships if requested
        if analyze_relationships and len(documents) > 1:
            for doc in documents:
                # Get all other documents
                other_docs = [d for d in documents if d != doc]
                
                # Extract relationships
                references = self.relationship_extractor.extract_references(
                    content=doc.content,
                    document_titles=[d.title for d in other_docs]
                )
                
                # Add relationships to metadata
                for ref in references:
                    # Find the referenced document
                    for other_doc in other_docs:
                        if other_doc.title == ref["title"]:
                            # Add relationship
                            doc.add_relationship(
                                target=other_doc,
                                relationship_type=ref["type"],
                                title=other_doc.title,
                                description=f"Auto-detected: {ref['context']}"
                            )
        
        # Create a collection if requested
        collection = None
        if create_collection and len(documents) > 0:
            collection_name = dir_path.name
            collection = Collection(name=collection_name, documents=documents)
        
        return documents, collection


class ContentEnhancementAgent:
    """
    Agent for enhancing document content.
    
    This agent provides capabilities for summarizing, transforming, and
    enhancing document content.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Initialize the content enhancement agent.
        
        Args:
            model: The AI model to use
            api_key: Optional API key for the model provider
            temperature: Temperature for generation
        """
        from pydanticai import PydanticAI
        
        self.ai = PydanticAI(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
    
    def generate_summary(
        self,
        document: Document,
        length: str = "medium",  # short, medium, long
        focus: Optional[str] = None
    ) -> str:
        """
        Generate a summary of the document content.
        
        Args:
            document: The document to summarize
            length: The desired length of the summary
            focus: Optional focus area for the summary
            
        Returns:
            A summary of the document
        """
        from pydantic import BaseModel
        
        class SummaryResult(BaseModel):
            summary: str
        
        length_guidance = {
            "short": "1-2 sentences",
            "medium": "1-2 paragraphs",
            "long": "3-5 paragraphs"
        }.get(length, "1-2 paragraphs")
        
        focus_instruction = f"with a focus on {focus}" if focus else ""
        
        system_prompt = f"""
        You are an expert document summarizer. Create a {length_guidance} summary of the 
        provided document {focus_instruction}. The summary should capture the main points
        and key information, while being concise and accurate.
        """
        
        user_prompt = f"Document Title: {document.title}\n\nContent:\n{document.content[:20000]}"
        
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=SummaryResult
        )
        
        return result.summary
    
    def generate_annotations(
        self,
        document: Document,
        annotation_type: str = "comments"  # comments, questions, references
    ) -> List[Dict[str, Any]]:
        """
        Generate annotations for a document.
        
        Args:
            document: The document to annotate
            annotation_type: The type of annotations to generate
            
        Returns:
            A list of annotation dictionaries
        """
        from pydantic import BaseModel
        
        class Annotation(BaseModel):
            text: str
            context: str
            position: Optional[int] = None
        
        class AnnotationResult(BaseModel):
            annotations: List[Annotation]
        
        type_instruction = {
            "comments": "insightful comments about key points or interesting aspects",
            "questions": "thought-provoking questions raised by the content",
            "references": "references to external sources or concepts mentioned"
        }.get(annotation_type, "insightful comments")
        
        system_prompt = f"""
        You are an expert document annotator. Generate 3-7 {type_instruction} for the
        provided document. For each annotation, include:
        1. The annotation text
        2. The relevant context from the document
        3. If possible, an approximate position (paragraph or section number)
        """
        
        user_prompt = f"Document Title: {document.title}\n\nContent:\n{document.content[:20000]}"
        
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=AnnotationResult
        )
        
        # Convert to simple dictionaries
        annotations = [
            {
                "text": anno.text,
                "context": anno.context,
                "position": anno.position,
                "type": annotation_type
            }
            for anno in result.annotations
        ]
        
        return annotations
    
    def suggest_improvements(
        self,
        document: Document,
        improvement_type: str = "general"  # general, structure, clarity, completeness
    ) -> List[Dict[str, Any]]:
        """
        Suggest improvements for a document.
        
        Args:
            document: The document to analyze
            improvement_type: The type of improvements to suggest
            
        Returns:
            A list of improvement suggestion dictionaries
        """
        from pydantic import BaseModel
        
        class Improvement(BaseModel):
            suggestion: str
            rationale: str
            location: Optional[str] = None
            priority: str  # high, medium, low
        
        class ImprovementResult(BaseModel):
            improvements: List[Improvement]
        
        type_instruction = {
            "general": "general improvements across all aspects",
            "structure": "improvements to the document's structure and organization",
            "clarity": "improvements to clarity and readability",
            "completeness": "additions or expansions to make the document more complete"
        }.get(improvement_type, "general improvements")
        
        system_prompt = f"""
        You are an expert document editor. Analyze the provided document and suggest
        {type_instruction}. For each suggestion, include:
        1. The specific improvement suggestion
        2. The rationale for this improvement
        3. Where in the document the improvement applies (if specific)
        4. The priority level (high, medium, low)
        
        Focus on the most impactful improvements that would significantly enhance the document.
        """
        
        user_prompt = f"Document Title: {document.title}\n\nContent:\n{document.content[:20000]}"
        
        result = self.ai.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=ImprovementResult
        )
        
        # Convert to simple dictionaries
        improvements = [
            {
                "suggestion": imp.suggestion,
                "rationale": imp.rationale,
                "location": imp.location,
                "priority": imp.priority,
                "type": improvement_type
            }
            for imp in result.improvements
        ]
        
        return improvements 