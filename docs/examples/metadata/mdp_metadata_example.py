#!/usr/bin/env python3
"""
Example script demonstrating how to use standardized metadata fields in MDP files.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datapack.mdp import MDPFile, write_mdp
from datapack.mdp.metadata import get_standard_fields


def main():
    """Main function to demonstrate MDP metadata usage."""
    # Get all standard metadata fields
    standard_fields = get_standard_fields()
    
    # Print available standard fields
    print("Available standard metadata fields:")
    for category, fields in {
        "Core Fields": ["title", "description", "version", "type"],
        "Authorship Fields": ["author", "contributors", "created_at", "updated_at"],
        "Classification Fields": ["tags", "category", "status"],
        "Source Fields": ["source_file", "source_type", "source_url"],
        "Relationship Fields": ["related_documents", "parent_document"],
    }.items():
        print(f"\n{category}:")
        for field in fields:
            field_info = standard_fields[field]
            print(f"  - {field}: {field_info['description']} ({field_info['type'].__name__})")
    
    # Create an MDP file with standard metadata fields
    metadata = {
        # Core fields
        "title": "Example Document with Standard Metadata",
        "description": "This document demonstrates the use of standard metadata fields",
        "version": "1.0.0",
        "type": "example",
        
        # Authorship fields
        "author": "Datapack Team",
        "contributors": ["Contributor 1", "Contributor 2"],
        "created_at": "2023-05-15",
        "updated_at": "2023-05-16",
        
        # Classification fields
        "tags": ["example", "metadata", "mdp"],
        "category": "documentation",
        "status": "published",
        
        # Source fields
        "source_file": "original_document.md",
        "source_type": "markdown",
        "source_url": "https://example.com/original",
        
        # Relationship fields
        "related_documents": ["doc1.mdp", "doc2.mdp"],
        "parent_document": "main_doc.mdp",
    }
    
    content = """# Example Document with Standard Metadata

This document demonstrates the use of standard metadata fields in MDP files.

## Purpose

The purpose of this document is to show how to use the standardized metadata fields
defined in the MDP module to create consistent and well-structured documents.

## Benefits of Standardized Metadata

1. **Consistency**: All documents follow the same structure
2. **Interoperability**: Different tools can work with the files predictably
3. **Validation**: Files can be validated against a schema
4. **Documentation**: Clear guidance for users creating MDP files
"""
    
    # Create the examples directory if it doesn't exist
    examples_dir = Path(__file__).parent
    output_path = examples_dir / "standard_metadata_example.mdp"
    
    # Write the MDP file
    mdp_file = write_mdp(output_path, metadata, content)
    
    print(f"\nCreated MDP file with standard metadata at: {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
    
    # Read back and display some metadata
    print("\nMetadata in the created file:")
    for category, fields in {
        "Core": ["title", "type"],
        "Authorship": ["author", "contributors"],
        "Classification": ["tags", "status"],
        "Source": ["source_type"],
        "Relationship": ["related_documents"],
    }.items():
        print(f"  {category}:")
        for field in fields:
            print(f"    - {field}: {mdp_file.metadata[field]}")


if __name__ == "__main__":
    main() 