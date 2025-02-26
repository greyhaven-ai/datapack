#!/usr/bin/env python3
"""
User-Friendly MDP API Examples

This script demonstrates how to use the enhanced user-friendly API
for working with MDP (Markdown Data Pack) files.

Usage:
    python user_friendly_api.py

Requirements:
    - datapack package
    - For PDF examples: pypdf
    - For web examples: requests, beautifulsoup4
"""

import os
import tempfile
from pathlib import Path

from datapack.mdp import Document, Collection
from datapack.mdp import convert_file, convert_directory


def print_section(title):
    """Print a section header for better readability."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def example_document_basics():
    """Demonstrate basic Document class operations."""
    print_section("Document Basics")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a new document
        doc = Document.create(
            title="Example Document",
            content="# Example Document\n\nThis is an example document with some content.",
            author="Datapack Team",
            tags=["example", "documentation"]
        )
        
        # Print the document metadata
        print(f"Document Title: {doc.title}")
        print(f"Document Author: {doc.author}")
        print(f"Document Tags: {doc.tags}")
        
        # Save the document
        doc_path = temp_path / "example.mdp"
        doc.save(doc_path)
        print(f"Document saved to: {doc_path}")
        
        # Load the document
        loaded_doc = Document.from_file(doc_path)
        print(f"Loaded document title: {loaded_doc.title}")
        
        # Modify the document
        loaded_doc.title = "Updated Title"
        loaded_doc.add_tag("updated")
        
        # Save the modified document
        loaded_doc.save()
        print(f"Updated document title: {loaded_doc.title}")
        print(f"Updated document tags: {loaded_doc.tags}")
        
        # Creating a document with direct metadata access
        doc2 = Document.create(title="Document with Custom Fields")
        doc2.metadata["x_priority"] = "high"
        doc2.metadata["x_department"] = "engineering"
        
        doc2_path = temp_path / "custom_fields.mdp"
        doc2.save(doc2_path)
        print(f"Document with custom fields saved to: {doc2_path}")


def example_relationships():
    """Demonstrate working with document relationships."""
    print_section("Document Relationships")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create some documents
        parent_doc = Document.create(
            title="Parent Document",
            content="# Parent Document\n\nThis is a parent document.",
            uuid="12345678-1234-5678-1234-567812345678"
        )
        
        child_doc1 = Document.create(
            title="Child Document 1",
            content="# Child Document 1\n\nThis is the first child document."
        )
        
        child_doc2 = Document.create(
            title="Child Document 2",
            content="# Child Document 2\n\nThis is the second child document."
        )
        
        # Create relationships
        child_doc1.add_relationship(
            parent_doc,
            relationship_type="parent",
            description="This is a child of the parent document"
        )
        
        child_doc2.add_relationship(
            parent_doc,
            relationship_type="parent",
            description="This is another child of the parent document"
        )
        
        # Also make the children related to each other
        child_doc1.add_relationship(
            child_doc2,
            relationship_type="related",
            description="These documents are related"
        )
        
        # Save the documents
        parent_doc.save(temp_path / "parent.mdp")
        child_doc1.save(temp_path / "child1.mdp")
        child_doc2.save(temp_path / "child2.mdp")
        
        # Now load the documents and check relationships
        reload_child1 = Document.from_file(temp_path / "child1.mdp")
        
        # Get related documents (uses the file path to find the relationships)
        related_docs = reload_child1.get_related_documents(base_path=temp_path)
        
        print(f"Related documents for '{reload_child1.title}':")
        for doc in related_docs:
            print(f"- {doc.title}")


def example_collection():
    """Demonstrate working with collections of documents."""
    print_section("Document Collections")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a collection
        collection = Collection("Example Collection")
        
        # Create some documents for the collection
        for i in range(1, 6):
            doc = Document.create(
                title=f"Document {i}",
                content=f"# Document {i}\n\nThis is document number {i} in the collection.",
                tags=[f"doc-{i}", "collection-example"]
            )
            collection.add_document(doc)
        
        # Save the collection
        collection_path = temp_path / "collection"
        os.makedirs(collection_path, exist_ok=True)
        collection.save_all(collection_path)
        
        print(f"Collection saved with {len(collection)} documents")
        
        # Load the collection from the directory
        loaded_collection = Collection.from_directory(collection_path)
        
        print(f"Loaded collection with {len(loaded_collection)} documents:")
        for doc in loaded_collection:
            print(f"- {doc.title}")
        
        # Find a document by title
        doc3 = loaded_collection.get_document_by_title("Document 3")
        if doc3:
            print(f"Found document: {doc3.title}")
            
        # Filter documents
        filtered_docs = loaded_collection.filter(
            lambda doc: "doc-2" in doc.tags or "doc-4" in doc.tags
        )
        
        print("Filtered documents:")
        for doc in filtered_docs:
            print(f"- {doc.title}")
        
        # Export the collection with a collection index
        export_path = temp_path / "exported_collection"
        loaded_collection.export(export_path)
        print(f"Collection exported to: {export_path}")


def example_conversion():
    """Demonstrate file conversion utilities."""
    print_section("File Conversion")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create some sample files to convert
        sample_files_dir = temp_path / "samples"
        os.makedirs(sample_files_dir, exist_ok=True)
        
        # Create a markdown file
        md_path = sample_files_dir / "sample.md"
        with open(md_path, "w") as f:
            f.write("# Sample Markdown\n\nThis is a sample markdown file.")
        
        # Create a text file
        txt_path = sample_files_dir / "sample.txt"
        with open(txt_path, "w") as f:
            f.write("Sample Text File\n\nThis is a sample text file.")
        
        # Create a nested directory with files
        nested_dir = sample_files_dir / "nested"
        os.makedirs(nested_dir, exist_ok=True)
        
        nested_path = nested_dir / "nested.md"
        with open(nested_path, "w") as f:
            f.write("# Nested File\n\nThis is a nested markdown file.")
        
        # Convert a single file
        output_dir = temp_path / "converted"
        os.makedirs(output_dir, exist_ok=True)
        
        converted_doc = convert_file(
            md_path,
            output_path=output_dir / "converted_sample.mdp",
            title="Converted Markdown",
            add_metadata={"status": "draft"}
        )
        
        print(f"Converted single file: {converted_doc.title}")
        print(f"Source file: {converted_doc.metadata.get('source_file')}")
        print(f"Source type: {converted_doc.metadata.get('source_type')}")
        
        # Convert a directory of files
        converted_docs = convert_directory(
            sample_files_dir,
            output_directory=output_dir,
            recursive=True,
            add_metadata={"batch_converted": True}
        )
        
        print(f"\nConverted {len(converted_docs)} files from directory:")
        for doc in converted_docs:
            print(f"- {doc.title} ({doc.path})")


def example_backward_compatibility():
    """Demonstrate backward compatibility with the original API."""
    print_section("Backward Compatibility")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Import the original API
        from datapack.mdp.core import MDPFile, read_mdp, write_mdp
        from datapack.mdp.metadata import create_metadata
        
        # Using the original API
        metadata = create_metadata(
            title="Legacy API Document",
            author="Datapack Team",
            tags=["legacy", "compatibility"]
        )
        
        content = "# Legacy API Document\n\nThis document was created with the original API."
        
        # Write using the original API
        legacy_path = temp_path / "legacy.mdp"
        mdp_file = write_mdp(legacy_path, metadata, content)
        
        print(f"Created document with original API: {mdp_file.metadata['title']}")
        
        # Read using the original API
        loaded_mdp = read_mdp(legacy_path)
        print(f"Loaded with original API: {loaded_mdp.metadata['title']}")
        
        # Now use the new API with the same file
        doc = Document.from_file(legacy_path)
        print(f"Loaded with new API: {doc.title}")
        
        # Create with new API and read with old API
        new_doc = Document.create(
            title="New API Document",
            content="# New API Document\n\nThis document was created with the new API.",
            author="Datapack Team"
        )
        
        new_path = temp_path / "new.mdp"
        new_doc.save(new_path)
        
        # Read with original API
        legacy_loaded = read_mdp(new_path)
        print(f"Created with new API, loaded with original API: {legacy_loaded.metadata['title']}")


def show_advanced_conversions():
    """Demo code for advanced conversions - doesn't run by default."""
    print_section("Advanced Conversions (Demo Code Only)")
    
    print("The following code shows how to use advanced conversion functions:")
    print("\n```python")
    print("from datapack.mdp import extract_text_from_pdf, import_website")
    print("")
    print("# Extract text from a PDF")
    print("pdf_doc = extract_text_from_pdf('document.pdf')")
    print("print(f'Extracted PDF: {pdf_doc.title}')")
    print("")
    print("# Import content from a website")
    print("web_doc = import_website('https://example.com')")
    print("print(f'Imported web page: {web_doc.title}')")
    print("```")
    print("\nNote: These functions require additional dependencies:")
    print("  - PDF extraction: pip install pypdf")
    print("  - Web importing: pip install requests beautifulsoup4")


if __name__ == "__main__":
    print("MDP User-Friendly API Examples")
    print("------------------------------")
    
    example_document_basics()
    example_relationships()
    example_collection()
    example_conversion()
    example_backward_compatibility()
    show_advanced_conversions()
    
    print("\nAll examples completed successfully!") 