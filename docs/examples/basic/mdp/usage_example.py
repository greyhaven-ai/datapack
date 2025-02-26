#!/usr/bin/env python3
"""
Example script demonstrating how to use the MDP file implementation.

This script shows how to create, read, and manipulate MDP files.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datapack.mdp import MDPFile, read_mdp, write_mdp
from datapack.mdp.metadata import create_metadata
from datapack.mdp.utils import convert_to_mdp, find_mdp_files


def create_example_mdp():
    """Create an example MDP file programmatically."""
    print("Creating an example MDP file programmatically...")
    
    # Create metadata
    metadata = create_metadata(
        title="Programmatically Created MDP File",
        description="This MDP file was created using the MDP API",
        author="Datapack Team",
        tags=["example", "api", "datapack"],
        metadata={
            "source": "api",
            "language": "en",
            "priority": "medium",
        }
    )
    
    # Create content
    content = """
# Programmatically Created MDP File

This MDP file was created using the MDP API. It demonstrates how to create
MDP files programmatically.

## Features

- Create MDP files with custom metadata
- Read and parse existing MDP files
- Extract and validate metadata
- Convert other file formats to MDP
    """
    
    # Write the MDP file
    output_path = Path(__file__).parent / "programmatic_example.mdp"
    mdp_file = write_mdp(output_path, metadata, content)
    
    print(f"Created MDP file at: {output_path}")
    return mdp_file


def read_example_mdp():
    """Read and display an existing MDP file."""
    print("\nReading an existing MDP file...")
    
    # Path to the example MDP file
    example_path = Path(__file__).parent / "example.mdp"
    
    # Read the MDP file
    mdp_file = read_mdp(example_path)
    
    # Display metadata
    print(f"Title: {mdp_file.metadata.get('title', 'No title')}")
    print(f"Author: {mdp_file.metadata.get('author', 'Unknown')}")
    print(f"Tags: {', '.join(mdp_file.metadata.get('tags', []))}")
    
    # Display content preview
    content_preview = mdp_file.content.strip()[:100] + "..." if len(mdp_file.content) > 100 else mdp_file.content
    print(f"Content preview: {content_preview}")
    
    return mdp_file


def convert_text_to_mdp():
    """Convert a text file to an MDP file."""
    print("\nConverting a text file to an MDP file...")
    
    # Create a temporary text file
    text_path = Path(__file__).parent / "temp.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write("""This is a simple text file.
        
It will be converted to an MDP file with metadata.

The conversion process will add YAML frontmatter at the top of the file.
""")
    
    # Convert the text file to an MDP file
    metadata = {
        "title": "Converted Text File",
        "description": "This text file was converted to an MDP file",
        "tags": ["text", "conversion", "example"]
    }
    
    mdp_file = convert_to_mdp(text_path, metadata=metadata)
    
    print(f"Converted text file to MDP: {mdp_file.path}")
    
    # Clean up the temporary text file
    os.remove(text_path)
    
    return mdp_file


def find_mdp_examples():
    """Find all MDP files in the examples directory."""
    print("\nFinding all MDP files in the examples directory...")
    
    examples_dir = Path(__file__).parent.parent
    mdp_files = find_mdp_files(examples_dir)
    
    print(f"Found {len(mdp_files)} MDP files:")
    for file_path in mdp_files:
        print(f"  - {file_path}")
    
    return mdp_files


def modify_mdp_file(mdp_file):
    """Modify an existing MDP file."""
    print("\nModifying an existing MDP file...")
    
    # Update metadata
    mdp_file.metadata["updated_at"] = "2023-05-16T09:30:00Z"
    mdp_file.metadata["tags"].append("modified")
    
    # Update content
    mdp_file.content += "\n\n## Added Section\n\nThis section was added programmatically."
    
    # Save the modified file
    modified_path = Path(__file__).parent / "modified_example.mdp"
    mdp_file.path = modified_path
    mdp_file.save()
    
    print(f"Modified MDP file saved to: {modified_path}")
    
    return mdp_file


def main():
    """Run the example script."""
    print("MDP File Format Example Script")
    print("=============================\n")
    
    # Create an example MDP file
    created_mdp = create_example_mdp()
    
    # Read an existing MDP file
    example_mdp = read_example_mdp()
    
    # Convert a text file to an MDP file
    converted_mdp = convert_text_to_mdp()
    
    # Find all MDP files in the examples directory
    find_mdp_examples()
    
    # Modify an existing MDP file
    modify_mdp_file(example_mdp)
    
    print("\nExample script completed successfully!")


if __name__ == "__main__":
    main() 