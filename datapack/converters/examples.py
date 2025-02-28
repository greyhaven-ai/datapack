"""
Examples demonstrating how to use the Datapack converters.

This module contains examples for converting various data formats to MDP.
"""

import os
import json
import tempfile
from pathlib import Path

from mdp import Document

from datapack.converters import json_to_mdp, xml_to_mdp, csv_to_mdp


def json_examples():
    """Examples of JSON to MDP conversion."""
    print("\n=== JSON to MDP Examples ===\n")
    
    # Example JSON data
    json_data = {
        "title": "Sample JSON Document",
        "description": "This is a sample JSON document for conversion to MDP",
        "author": "Datapack Team",
        "created_at": "2023-05-15",
        "version": "1.0.0",
        "tags": ["json", "example", "datapack"],
        "content": {
            "sections": [
                {
                    "heading": "Introduction",
                    "text": "This is the introduction section."
                },
                {
                    "heading": "Main Content",
                    "text": "This is the main content section.",
                    "subsections": [
                        {"heading": "Subsection 1", "text": "Subsection 1 content"},
                        {"heading": "Subsection 2", "text": "Subsection 2 content"}
                    ]
                },
                {
                    "heading": "Conclusion",
                    "text": "This is the conclusion."
                }
            ]
        }
    }
    
    # Convert from dictionary
    print("1. Converting from Python dictionary...")
    doc1 = json_to_mdp(json_data)
    print(f"Created document: {doc1.title}")
    print(f"Metadata: {doc1.metadata}")
    print(f"Content preview: {doc1.content[:100]}...\n")
    
    # Convert from JSON string
    print("2. Converting from JSON string...")
    json_string = json.dumps(json_data)
    doc2 = json_to_mdp(json_string)
    print(f"Created document: {doc2.title}\n")
    
    # Save to a file and convert from file
    print("3. Converting from JSON file...")
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
        json.dump(json_data, f)
        temp_path = f.name
    
    doc3 = json_to_mdp(temp_path, output_path=temp_path + ".mdp")
    print(f"Created document: {doc3.title}")
    print(f"Saved to: {temp_path}.mdp\n")
    
    # Clean up
    os.unlink(temp_path)
    if os.path.exists(temp_path + ".mdp"):
        os.unlink(temp_path + ".mdp")


def xml_examples():
    """Examples of XML to MDP conversion."""
    print("\n=== XML to MDP Examples ===\n")
    
    # Example XML data
    xml_data = """
    <document>
        <title>Sample XML Document</title>
        <metadata>
            <author>Datapack Team</author>
            <created>2023-05-15</created>
            <version>1.0.0</version>
            <tags>
                <tag>xml</tag>
                <tag>example</tag>
                <tag>datapack</tag>
            </tags>
        </metadata>
        <content>
            <section>
                <heading>Introduction</heading>
                <text>This is the introduction section.</text>
            </section>
            <section>
                <heading>Main Content</heading>
                <text>This is the main content section.</text>
                <subsection>
                    <heading>Subsection 1</heading>
                    <text>Subsection 1 content</text>
                </subsection>
                <subsection>
                    <heading>Subsection 2</heading>
                    <text>Subsection 2 content</text>
                </subsection>
            </section>
            <section>
                <heading>Conclusion</heading>
                <text>This is the conclusion.</text>
            </section>
        </content>
    </document>
    """
    
    # Convert from XML string
    print("1. Converting from XML string...")
    doc1 = xml_to_mdp(xml_data)
    print(f"Created document: {doc1.title}")
    print(f"Metadata: {doc1.metadata}")
    print(f"Content preview: {doc1.content[:100]}...\n")
    
    # Save to a file and convert from file
    print("2. Converting from XML file...")
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False, mode='w') as f:
        f.write(xml_data)
        temp_path = f.name
    
    doc2 = xml_to_mdp(temp_path, output_path=temp_path + ".mdp")
    print(f"Created document: {doc2.title}")
    print(f"Saved to: {temp_path}.mdp\n")
    
    # Convert with custom options
    print("3. Converting with custom options...")
    doc3 = xml_to_mdp(
        xml_data,
        metadata={"title": "Custom XML Title", "tags": ["custom", "xml"]},
        extract_metadata=False,
        max_depth=2
    )
    print(f"Created document: {doc3.title}")
    print(f"Metadata: {doc3.metadata}")
    
    # Clean up
    os.unlink(temp_path)
    if os.path.exists(temp_path + ".mdp"):
        os.unlink(temp_path + ".mdp")


def csv_examples():
    """Examples of CSV to MDP conversion."""
    print("\n=== CSV to MDP Examples ===\n")
    
    # Example CSV data
    csv_data = """
    name,age,email,city,score
    John Doe,32,john@example.com,New York,85
    Jane Smith,28,jane@example.com,San Francisco,92
    Bob Johnson,45,bob@example.com,Chicago,78
    Alice Brown,39,alice@example.com,Los Angeles,95
    Charlie Wilson,22,charlie@example.com,Miami,81
    """
    
    # Convert from CSV string
    print("1. Converting from CSV string...")
    doc1 = csv_to_mdp(csv_data.strip())
    print(f"Created document: {doc1.title}")
    print(f"Metadata: {doc1.metadata}")
    print(f"Content preview: {doc1.content[:100]}...\n")
    
    # Save to a file and convert from file
    print("2. Converting from CSV file...")
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        f.write(csv_data)
        temp_path = f.name
    
    doc2 = csv_to_mdp(temp_path, output_path=temp_path + ".mdp", include_stats=True)
    print(f"Created document: {doc2.title}")
    print(f"Saved to: {temp_path}.mdp\n")
    
    # Convert with custom options
    print("3. Converting with custom options...")
    doc3 = csv_to_mdp(
        csv_data.strip(),
        metadata={"title": "Custom CSV Title", "tags": ["custom", "csv"]},
        extract_metadata=False,
        max_rows=3,
        has_header=True
    )
    print(f"Created document: {doc3.title}")
    print(f"Metadata: {doc3.metadata}")
    
    # Clean up
    os.unlink(temp_path)
    if os.path.exists(temp_path + ".mdp"):
        os.unlink(temp_path + ".mdp")


def run_all_examples():
    """Run all converter examples."""
    print("Datapack Converters Examples")
    print("===========================")
    
    json_examples()
    xml_examples()
    csv_examples()
    
    print("\nAll examples completed successfully!")


if __name__ == "__main__":
    run_all_examples() 