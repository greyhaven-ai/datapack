"""
Examples of using Datapack AI workflows.

This module provides examples of how to use the AI-powered document processing
workflows in real-world scenarios.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from mdp import Document, Collection
from datapack.workflows.ai_processing import (
    process_document,
    process_documents,
    convert_directory
)
from datapack.ai.models import AISettings, AIModelConfig


def example_process_single_document(
    document_path: str, 
    output_path: Optional[str] = None,
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None
) -> Document:
    """
    Example of processing a single document.
    
    Args:
        document_path: Path to the document to process
        output_path: Optional path to save the processed document
        settings: Optional AI settings to configure the processing
        
    Returns:
        The processed Document
    """
    print(f"Processing document: {document_path}")
    
    # Configure AI settings
    if not settings:
        settings = AISettings(
            default_model=AIModelConfig(
                model_name="gpt-4",
                provider="openai",
                temperature=0.0
            )
        )
    
    # Process the document
    document = process_document(
        document=document_path,
        extract_metadata=True,
        extract_insights=True,
        extract_relationships=False,
        enhance_content=True,
        settings=settings
    )
    
    # Print extracted metadata
    print("\nExtracted Metadata:")
    # Standard metadata field groups for organized display
    metadata_groups = {
        "Core": ["title", "version", "context"],
        "Identification": ["uuid", "uri", "local_path", "cid"],
        "Collection": ["collection", "collection_id", "collection_id_type", "position"],
        "Authorship": ["author", "contributors", "created_at", "updated_at"],
        "Classification": ["tags", "status"],
        "Source": ["source_file", "source_type", "source_url"]
    }
    
    # Print metadata by group
    for group, fields in metadata_groups.items():
        has_fields = any(field in document.metadata for field in fields)
        if has_fields:
            print(f"  {group} fields:")
            for field in fields:
                if field in document.metadata:
                    print(f"    {field}: {document.metadata[field]}")
    
    # Print any fields that aren't in our groups (custom fields)
    custom_fields = [k for k in document.metadata.keys() 
                    if k not in sum(metadata_groups.values(), []) and 
                       k not in ['insights', 'structure', 'enhancement', 'relationships']]
    if custom_fields:
        print("  Custom fields:")
        for field in custom_fields:
            print(f"    {field}: {document.metadata[field]}")
    
    # Print key insights if available
    if 'insights' in document.metadata:
        print("\nKey Insights:")
        for insight in document.metadata['insights']:
            print(f"  - {insight.get('insight', '')}")
    
    # Print enhancement info if available
    if 'enhancement' in document.metadata:
        print("\nEnhancement:")
        print(f"  Confidence: {document.metadata['enhancement'].get('confidence', 0)}")
        print(f"  Changes made: {len(document.metadata['enhancement'].get('changes', []))}")
    
    # Save the document if output path provided
    if output_path:
        save_path = Path(output_path)
        if save_path.is_dir():
            save_path = save_path / f"{document.title}.mdp"
        
        document.path = save_path
        document.save()
        print(f"\nSaved document to: {save_path}")
    
    return document


def example_process_document_collection(
    directory_path: str,
    output_directory: Optional[str] = None,
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None
) -> Collection:
    """
    Example of processing a directory of documents as a collection.
    
    Args:
        directory_path: Path to directory containing documents
        output_directory: Optional path to save processed documents
        settings: Optional AI settings to configure the processing
        
    Returns:
        The processed Collection
    """
    print(f"Processing documents in: {directory_path}")
    
    # Configure AI settings
    if not settings:
        settings = AISettings(
            default_model=AIModelConfig(
                model_name="gpt-4",
                provider="openai",
                temperature=0.0
            ),
            relationship_model=AIModelConfig(
                model_name="gpt-4",
                provider="openai",
                temperature=0.3
            )
        )
    
    # Find all markdown files in the directory
    dir_path = Path(directory_path)
    files = list(dir_path.glob("*.md"))
    
    print(f"Found {len(files)} markdown files")
    
    # Create Document objects
    documents = [Document.from_file(file) for file in files]
    
    # Create a Collection
    collection = Collection(
        name=dir_path.name,
        documents=documents
    )
    
    # Process the collection
    processed_collection = process_documents(
        collection=collection,
        extract_metadata=True,
        extract_insights=True,
        extract_relationships=True,
        enhance_content=False,
        max_concurrent=3,
        settings=settings
    )
    
    # Print collection information
    print(f"\nProcessed collection: {processed_collection.name}")
    print(f"Documents: {len(processed_collection.documents)}")
    
    # Print relationships if found
    relationship_count = 0
    for doc in processed_collection.documents:
        if 'relationships' in doc.metadata and doc.metadata['relationships']:
            relationship_count += len(doc.metadata['relationships'])
    
    print(f"Discovered {relationship_count} relationships between documents")
    
    # Save the collection if output directory provided
    if output_directory:
        output_dir = Path(output_directory)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual documents
        for doc in processed_collection.documents:
            doc_path = output_dir / f"{doc.title}.mdp"
            doc.path = doc_path
            doc.save()
        
        # Save collection
        collection_path = output_dir / f"{processed_collection.name}_collection.json"
        processed_collection.save(collection_path)
        
        print(f"\nSaved collection to: {collection_path}")
    
    return processed_collection


def example_convert_and_process_directory(
    source_directory: str,
    output_directory: str,
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None
) -> tuple:
    """
    Example of converting files to MDP format and processing them.
    
    Args:
        source_directory: Directory containing files to convert
        output_directory: Directory to save processed documents
        settings: Optional AI settings to configure the processing
        
    Returns:
        A tuple of (documents, collection)
    """
    print(f"Converting and processing files in: {source_directory}")
    
    # Configure AI settings
    if not settings:
        settings = AISettings(
            default_model=AIModelConfig(
                model_name="gpt-4",
                provider="openai",
                temperature=0.0
            )
        )
    
    # Convert and process files
    documents, collection = convert_directory(
        source_directory=source_directory,
        output_directory=output_directory,
        file_pattern="*.{md,txt,pdf,docx}",  # Process multiple file types
        recursive=True,
        create_collection=True,
        extract_metadata=True,
        extract_insights=True,
        extract_relationships=True,
        max_concurrent=3,
        settings=settings
    )
    
    # Print results
    print(f"\nConverted and processed {len(documents)} documents")
    
    if collection:
        print(f"Created collection: {collection.name}")
        print(f"Collection saved to: {output_directory}/{collection.name}_collection.json")
    
    return documents, collection


async def advanced_example_custom_processing_pipeline(
    settings: Optional[Union[AISettings, Dict[str, Any]]] = None
):
    """
    Advanced example showing a custom document processing pipeline.
    
    Args:
        settings: Optional AI settings to configure the processing
    """
    # Configure AI settings
    if not settings:
        settings = AISettings(
            default_model=AIModelConfig(
                model_name="gpt-4",
                provider="openai",
                temperature=0.0
            ),
            metadata_model=AIModelConfig(
                model_name="gpt-3.5-turbo",
                provider="openai",
                temperature=0.3
            ),
            enhancement_model=AIModelConfig(
                model_name="gpt-4",
                provider="openai",
                temperature=0.7
            )
        )
    
    print("Starting advanced document processing pipeline")
    
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Load documents from different sources
        documents = []
        
        # Load from a markdown file
        if os.path.exists("example.md"):
            doc1 = Document.from_file("example.md")
            documents.append(doc1)
        else:
            # Create a sample document if file doesn't exist
            doc1 = Document(
                content="# Sample Document\n\nThis is a sample document created for the advanced example.",
                metadata={"title": "Sample Document"}
            )
            documents.append(doc1)
        
        # Create another sample document
        doc2 = Document(
            content="# Another Sample\n\nThis document references the sample document.",
            metadata={"title": "Another Sample"}
        )
        documents.append(doc2)
        
        # 2. Process each document with different parameters
        processed_docs = []
        
        # Process first document with metadata extraction only
        print("\nProcessing first document (metadata only)")
        deps1 = DocumentDependencies(
            document=doc1,
            model_name="openai:gpt-4o",
            temperature=0.0
        )
        
        metadata_result = await metadata_extraction_agent.run(
            doc1.content,
            deps=deps1
        )
        
        # Update document metadata
        metadata_dict = metadata_result.data.dict(exclude_none=True)
        for key, value in metadata_dict.items():
            if value and key != "confidence":
                doc1.metadata[key] = value
        
        processed_docs.append(doc1)
        
        # Process second document with content enhancement
        print("Processing second document (content enhancement)")
        deps2 = DocumentDependencies(
            document=doc2,
            model_name="openai:gpt-4o",
            temperature=0.3
        )
        
        enhancement_result = await content_enhancement_agent.run(
            doc2.content,
            deps=deps2
        )
        
        # Update document content
        doc2.content = enhancement_result.data.enhanced_content
        
        # Add enhancement info to metadata
        doc2.metadata["enhancement"] = {
            "changes": enhancement_result.data.changes_made,
            "confidence": enhancement_result.data.confidence
        }
        
        processed_docs.append(doc2)
        
        # 3. Create a collection and process for relationships
        print("Creating collection and processing relationships")
        collection = Collection(
            name="Advanced Example Collection",
            documents=processed_docs
        )
        
        # Process the collection to find relationships
        processed_collection = await process_collection(
            collection=collection,
            extract_metadata=False,  # Already extracted
            extract_insights=False,  # Skip for this example
            extract_relationships=True,  # Only extract relationships
            enhance_content=False,  # Already enhanced
            max_concurrent=2
        )
        
        # 4. Generate a custom report
        print("\nGenerating custom processing report")
        report = "# Document Processing Report\n\n"
        report += f"Processed {len(processed_collection.documents)} documents\n\n"
        
        for doc in processed_collection.documents:
            report += f"## {doc.title}\n\n"
            
            # Add metadata summary
            report += "### Metadata\n\n"
            for key, value in doc.metadata.items():
                if key not in ['insights', 'structure', 'enhancement', 'relationships']:
                    report += f"- **{key}**: {value}\n"
            
            # Add relationships if any
            if 'relationships' in doc.metadata and doc.metadata['relationships']:
                report += "\n### Relationships\n\n"
                for rel in doc.metadata['relationships']:
                    report += f"- **{rel.get('type', 'Related')}** to {rel.get('title', 'Unknown')}\n"
            
            # Add enhancement info if available
            if 'enhancement' in doc.metadata:
                report += "\n### Enhancements\n\n"
                report += f"- **Confidence**: {doc.metadata['enhancement'].get('confidence', 0)}\n"
                report += f"- **Changes**: {len(doc.metadata['enhancement'].get('changes', []))}\n"
            
            report += "\n"
        
        # Save the report
        report_path = Path(temp_dir) / "processing_report.md"
        with open(report_path, "w") as f:
            f.write(report)
        
        print(f"Report generated at: {report_path}")
        print("Advanced processing pipeline completed")
        
        # Return the processed collection
        return processed_collection


def run_advanced_example():
    """Run the advanced example."""
    asyncio.run(advanced_example_custom_processing_pipeline())


if __name__ == "__main__":
    # Uncomment one of these examples to run it
    
    # Example 1: Process a single document
    # example_process_single_document("example.md", "output")
    
    # Example 2: Process a collection of documents
    # example_process_document_collection("docs", "output")
    
    # Example 3: Convert and process a directory
    # example_convert_and_process_directory("source", "output")
    
    # Example 4: Advanced custom pipeline
    # run_advanced_example()
    
    print("Uncomment an example to run it") 