"""
Example script demonstrating document relationships and collections in MDP files.

This script shows how to:
1. Create documents with UUIDs
2. Create documents in a collection
3. Create relationships between documents
4. Navigate document relationships
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datapack.mdp import (
    MDPFile,
    read_mdp,
    write_mdp,
    create_metadata,
    generate_uuid,
    create_uri,
    create_relationship,
    add_relationship_to_metadata,
    create_collection_metadata,
    find_related_documents,
    find_collection_members,
    create_collection,
    get_collection_hierarchy
)


def example_basic_uuid():
    """Example of creating documents with UUIDs."""
    print("\n=== Example: Basic UUID Usage ===")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a document with auto-generated UUID
        doc1_metadata = create_metadata(title="Document with UUID")
        doc1_path = Path(temp_dir) / "doc1.mdp"
        doc1 = write_mdp(
            doc1_path,
            doc1_metadata,
            "# Document with UUID\n\nThis document has an auto-generated UUID."
        )
        
        # Create a document with specific UUID
        specific_uuid = generate_uuid()  # Generate it separately
        doc2_metadata = create_metadata(
            title="Document with Specific UUID",
            uuid=specific_uuid
        )
        doc2_path = Path(temp_dir) / "doc2.mdp"
        doc2 = write_mdp(
            doc2_path,
            doc2_metadata,
            "# Document with Specific UUID\n\nThis document has a specific UUID."
        )
        
        # Read and display UUIDs
        print(f"Document 1 UUID: {doc1.metadata['uuid']}")
        print(f"Document 2 UUID: {doc2.metadata['uuid']}")


def example_relationships():
    """Example of creating and using document relationships."""
    print("\n=== Example: Document Relationships ===")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a parent document
        parent_metadata = create_metadata(title="Parent Document")
        parent_path = temp_path / "parent.mdp"
        parent = write_mdp(
            parent_path,
            parent_metadata,
            "# Parent Document\n\nThis is a parent document with children."
        )
        
        # Create first child document with relationship to parent
        child1_metadata = create_metadata(title="Child Document 1")
        child1_metadata = add_relationship_to_metadata(
            child1_metadata,
            parent.metadata["uuid"],
            "parent",
            title="Parent Document"
        )
        child1_path = temp_path / "child1.mdp"
        child1 = write_mdp(
            child1_path,
            child1_metadata,
            "# Child Document 1\n\nThis document references its parent."
        )
        
        # Create second child document
        child2_metadata = create_metadata(title="Child Document 2")
        child2_metadata = add_relationship_to_metadata(
            child2_metadata,
            parent.metadata["uuid"],
            "parent",
            title="Parent Document"
        )
        child2_path = temp_path / "child2.mdp"
        child2 = write_mdp(
            child2_path,
            child2_metadata,
            "# Child Document 2\n\nThis document also references its parent."
        )
        
        # Add relationships from parent to children
        parent_metadata = add_relationship_to_metadata(
            parent.metadata,
            child1.metadata["uuid"],
            "child",
            title="Child Document 1"
        )
        parent_metadata = add_relationship_to_metadata(
            parent_metadata,
            child2.metadata["uuid"],
            "child", 
            title="Child Document 2"
        )
        parent = write_mdp(parent_path, parent_metadata, parent.content)
        
        # Create a related document using a relative path
        related_metadata = create_metadata(title="Related Document")
        related_metadata = add_relationship_to_metadata(
            related_metadata,
            "parent.mdp",  # Using path instead of UUID
            "related",
            title="Parent Document",
            is_uri=False  # This is a path, not a URI
        )
        related_path = temp_path / "related.mdp"
        related = write_mdp(
            related_path,
            related_metadata,
            "# Related Document\n\nThis document has a related reference to the parent."
        )
        
        # Find children of the parent
        children = find_related_documents(parent, relationship_type="child")
        print(f"Found {len(children)} children of the parent document:")
        for i, child in enumerate(children):
            print(f"  {i+1}. {child.metadata['title']} (UUID: {child.metadata['uuid']})")
        
        # Get hierarchy information for child1
        hierarchy = get_collection_hierarchy(child1)
        print(f"\nHierarchy for '{child1.metadata['title']}':")
        if hierarchy["parent"]:
            print(f"  Parent: {hierarchy['parent'].metadata['title']}")
        print(f"  Siblings: {len(hierarchy['siblings'])}")
        print(f"  Children: {len(hierarchy['children'])}")


def example_collections():
    """Example of creating and using document collections."""
    print("\n=== Example: Document Collections ===")
    
    # Create a temporary directory for our collections
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a collection directory
        collection_dir = Path(temp_dir) / "tutorial"
        collection_dir.mkdir(exist_ok=True)
        
        # Create a collection with documents
        collection_id = generate_uuid()[:8]  # Short ID for the collection
        documents = [
            {
                "metadata": {
                    "title": "Introduction to MDP",
                    "context": "Overview of the MDP format"
                },
                "content": "# Introduction to MDP\n\nThis document introduces the MDP format.",
                "filename": "01_introduction.mdp"
            },
            {
                "metadata": {
                    "title": "Creating MDP Files",
                    "context": "How to create MDP files"
                },
                "content": "# Creating MDP Files\n\nThis document explains how to create MDP files.",
                "filename": "02_creating.mdp"
            },
            {
                "metadata": {
                    "title": "Working with Collections",
                    "context": "How to use collections in MDP"
                },
                "content": "# Working with Collections\n\nThis document explains how to use collections in MDP.",
                "filename": "03_collections.mdp"
            }
        ]
        
        # Create the collection
        collection = create_collection(
            collection_dir,
            "MDP Tutorial",
            collection_id,
            documents
        )
        
        print(f"Created collection: MDP Tutorial (ID: {collection_id})")
        print(f"Number of documents: {len(collection)}")
        
        # Find members of the collection
        members = find_collection_members(
            collection_dir,
            "MDP Tutorial",
            collection_id
        )
        
        print("\nCollection members (in order):")
        for i, doc in enumerate(members):
            print(f"  {i+1}. {doc.metadata['title']} (Position: {doc.metadata['position']})")
        
        # Create a standalone document that references the collection
        standalone_metadata = create_collection_metadata(
            "MDP Tutorial",
            collection_id=collection_id,
            title="Advanced Topics",
            context="Advanced topics in MDP"
        )
        
        # Add a relationship to the first document in the collection
        standalone_metadata = add_relationship_to_metadata(
            standalone_metadata,
            collection[0].metadata["uuid"],
            "related",
            title=collection[0].metadata["title"]
        )
        
        standalone_path = Path(temp_dir) / "advanced.mdp"
        standalone = write_mdp(
            standalone_path,
            standalone_metadata,
            "# Advanced Topics\n\nThis document covers advanced topics and references the introductory document."
        )
        
        print(f"\nCreated standalone document: {standalone.metadata['title']}")
        print(f"Part of collection: {standalone.metadata['collection']}")
        print(f"Related to: {standalone.metadata['relationships'][0]['title']}")


def example_uri_references():
    """Example of using URI references."""
    print("\n=== Example: URI References ===")
    
    # Create a URI for a document
    uri = create_uri("example-org", "mdp-project", "documentation/getting-started")
    print(f"Created URI: {uri}")
    
    # Create a document that references an external document via URI
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create document with URI reference
        doc_metadata = create_metadata(title="Document with URI Reference")
        doc_metadata = add_relationship_to_metadata(
            doc_metadata,
            uri,
            "reference",
            title="External Getting Started Guide",
            description="Official documentation for MDP format",
            is_uri=True
        )
        
        doc_path = Path(temp_dir) / "doc_with_uri.mdp"
        doc = write_mdp(
            doc_path,
            doc_metadata,
            "# Document with URI Reference\n\nThis document references an external resource."
        )
        
        # Display the reference
        print(f"Document: {doc.metadata['title']}")
        for rel in doc.metadata['relationships']:
            print(f"  References: {rel['title']} ({rel['uri']})")
            print(f"  Description: {rel['description']}")


if __name__ == "__main__":
    example_basic_uuid()
    example_relationships()
    example_collections()
    example_uri_references() 