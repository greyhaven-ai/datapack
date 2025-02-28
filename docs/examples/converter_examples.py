#!/usr/bin/env python3
"""
Converter Examples

This script demonstrates how to use the various converters in the datapack package
to convert different data formats to MDP files.
"""

import os
import json
import csv
import yaml
import tempfile
from pathlib import Path

from datapack.converters import (
    json_to_mdp,
    xml_to_mdp,
    csv_to_mdp,
    yaml_to_mdp,
    markdown_to_mdp,
)

# Try to import PDF converter if available
try:
    from datapack.converters import pdf_to_mdp
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PDF support not available. Install with 'pip install datapack[pdf]'")

# Create a directory for output files
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)

def example_json_converter():
    """Example of converting JSON to MDP."""
    print("\n=== JSON to MDP Conversion ===")
    
    # Sample JSON data
    json_data = {
        "title": "Sample JSON Document",
        "author": "Datapack User",
        "created_at": "2023-05-15T10:30:00",
        "data": {
            "items": [
                {"id": 1, "name": "Item 1", "value": 10.5},
                {"id": 2, "name": "Item 2", "value": 20.75},
                {"id": 3, "name": "Item 3", "value": 30.0}
            ],
            "total": 61.25,
            "currency": "USD"
        },
        "tags": ["sample", "json", "datapack"]
    }
    
    # Convert JSON to MDP
    output_path = OUTPUT_DIR / "json_example.mdp"
    doc = json_to_mdp(
        json_data=json_data,
        output_path=output_path,
        extract_metadata=True
    )
    
    print(f"Converted JSON to MDP: {output_path}")
    print(f"Document title: {doc.metadata.get('title')}")
    print(f"Document tags: {doc.metadata.get('tags')}")
    
    # You can also convert from a JSON string
    json_str = json.dumps(json_data)
    doc = json_to_mdp(json_str)
    print(f"Converted JSON string to MDP document with ID: {doc.id}")
    
    # Or from a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        temp_file = f.name
    
    try:
        doc = json_to_mdp(temp_file)
        print(f"Converted JSON file to MDP document with ID: {doc.id}")
    finally:
        os.unlink(temp_file)

def example_xml_converter():
    """Example of converting XML to MDP."""
    print("\n=== XML to MDP Conversion ===")
    
    # Sample XML data
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <document>
        <metadata>
            <title>Sample XML Document</title>
            <author>Datapack User</author>
            <created>2023-05-16T14:45:00</created>
            <tags>
                <tag>sample</tag>
                <tag>xml</tag>
                <tag>datapack</tag>
            </tags>
        </metadata>
        <content>
            <section id="intro">
                <heading>Introduction</heading>
                <paragraph>This is a sample XML document for conversion.</paragraph>
            </section>
            <section id="data">
                <heading>Data</heading>
                <items>
                    <item id="1" value="10.5">Item 1</item>
                    <item id="2" value="20.75">Item 2</item>
                    <item id="3" value="30.0">Item 3</item>
                </items>
            </section>
        </content>
    </document>
    """
    
    # Convert XML to MDP
    output_path = OUTPUT_DIR / "xml_example.mdp"
    doc = xml_to_mdp(
        xml_data=xml_data,
        output_path=output_path,
        extract_metadata=True,
        metadata_xpath={
            "title": "//metadata/title",
            "author": "//metadata/author",
            "created_at": "//metadata/created",
            "tags": "//metadata/tags/tag"
        }
    )
    
    print(f"Converted XML to MDP: {output_path}")
    print(f"Document title: {doc.metadata.get('title')}")
    print(f"Document tags: {doc.metadata.get('tags')}")
    
    # You can also convert from a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_data)
        temp_file = f.name
    
    try:
        doc = xml_to_mdp(temp_file)
        print(f"Converted XML file to MDP document with ID: {doc.id}")
    finally:
        os.unlink(temp_file)

def example_csv_converter():
    """Example of converting CSV to MDP."""
    print("\n=== CSV to MDP Conversion ===")
    
    # Sample CSV data
    csv_data = """id,name,value,category
1,Item 1,10.5,A
2,Item 2,20.75,B
3,Item 3,30.0,A
4,Item 4,15.25,C
5,Item 5,25.5,B
"""
    
    # Convert CSV to MDP
    output_path = OUTPUT_DIR / "csv_example.mdp"
    doc = csv_to_mdp(
        csv_data=csv_data,
        output_path=output_path,
        metadata={
            "title": "Sample CSV Document",
            "author": "Datapack User",
            "created_at": "2023-05-17T09:15:00",
            "tags": ["sample", "csv", "datapack"]
        },
        include_stats=True
    )
    
    print(f"Converted CSV to MDP: {output_path}")
    print(f"Document title: {doc.metadata.get('title')}")
    print(f"Document tags: {doc.metadata.get('tags')}")
    
    # You can also convert from a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_data)
        temp_file = f.name
    
    try:
        doc = csv_to_mdp(
            temp_file,
            metadata={"title": "CSV File Example"}
        )
        print(f"Converted CSV file to MDP document with ID: {doc.id}")
    finally:
        os.unlink(temp_file)

def example_yaml_converter():
    """Example of converting YAML to MDP."""
    print("\n=== YAML to MDP Conversion ===")
    
    # Sample YAML data
    yaml_data = """
title: Sample YAML Document
author: Datapack User
created_at: 2023-05-18T11:20:00
tags:
  - sample
  - yaml
  - datapack

data:
  items:
    - id: 1
      name: Item 1
      value: 10.5
    - id: 2
      name: Item 2
      value: 20.75
    - id: 3
      name: Item 3
      value: 30.0
  total: 61.25
  currency: USD
"""
    
    # Convert YAML to MDP
    output_path = OUTPUT_DIR / "yaml_example.mdp"
    doc = yaml_to_mdp(
        yaml_data=yaml_data,
        output_path=output_path,
        extract_metadata=True
    )
    
    print(f"Converted YAML to MDP: {output_path}")
    print(f"Document title: {doc.metadata.get('title')}")
    print(f"Document tags: {doc.metadata.get('tags')}")
    
    # You can also convert from a Python dict
    yaml_dict = yaml.safe_load(yaml_data)
    doc = yaml_to_mdp(yaml_dict)
    print(f"Converted YAML dict to MDP document with ID: {doc.id}")
    
    # Or from a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_data)
        temp_file = f.name
    
    try:
        doc = yaml_to_mdp(temp_file)
        print(f"Converted YAML file to MDP document with ID: {doc.id}")
    finally:
        os.unlink(temp_file)

def example_markdown_converter():
    """Example of converting Markdown to MDP."""
    print("\n=== Markdown to MDP Conversion ===")
    
    # Sample Markdown data with frontmatter
    markdown_data = """---
title: Sample Markdown Document
author: Datapack User
date: 2023-05-19
tags: [sample, markdown, datapack]
---

# Introduction

This is a sample Markdown document for conversion to MDP format.

## Features

- Frontmatter metadata extraction
- Markdown content preservation
- Automatic title detection

## Code Example

```python
def hello_world():
    print("Hello, world!")
```

Tags: #sample #markdown #datapack
"""
    
    # Convert Markdown to MDP
    output_path = OUTPUT_DIR / "markdown_example.mdp"
    doc = markdown_to_mdp(
        markdown_data=markdown_data,
        output_path=output_path,
        extract_metadata=True
    )
    
    print(f"Converted Markdown to MDP: {output_path}")
    print(f"Document title: {doc.metadata.get('title')}")
    print(f"Document tags: {doc.metadata.get('tags')}")
    
    # You can also convert from a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(markdown_data)
        temp_file = f.name
    
    try:
        doc = markdown_to_mdp(
            temp_file,
            preserve_frontmatter=True
        )
        print(f"Converted Markdown file to MDP document with ID: {doc.id}")
    finally:
        os.unlink(temp_file)
    
    # Example without frontmatter
    markdown_no_frontmatter = """# Simple Markdown Document

This is a simple markdown document without frontmatter.

## Section 1

Content of section 1.

## Section 2

Content of section 2.
"""
    
    doc = markdown_to_mdp(
        markdown_data=markdown_no_frontmatter,
        metadata={
            "author": "Datapack User",
            "tags": ["simple", "markdown"]
        }
    )
    print(f"Converted simple Markdown to MDP document with ID: {doc.id}")

def example_pdf_converter():
    """Example of converting PDF to MDP."""
    if not PDF_SUPPORT:
        print("\n=== PDF to MDP Conversion ===")
        print("PDF support not available. Install with 'pip install datapack[pdf]'")
        return
    
    print("\n=== PDF to MDP Conversion ===")
    print("Note: This example requires a PDF file to convert.")
    
    # For this example, we'll need an actual PDF file
    # We'll check if a sample PDF exists, otherwise skip this example
    sample_pdf = Path("./sample.pdf")
    if not sample_pdf.exists():
        print(f"Sample PDF file not found at {sample_pdf}. Skipping PDF conversion example.")
        print("To run this example, place a PDF file named 'sample.pdf' in the current directory.")
        return
    
    # Convert PDF to MDP
    output_path = OUTPUT_DIR / "pdf_example.mdp"
    doc = pdf_to_mdp(
        pdf_data=sample_pdf,
        output_path=output_path,
        extract_metadata=True,
        max_pages=5  # Limit to first 5 pages
    )
    
    print(f"Converted PDF to MDP: {output_path}")
    print(f"Document title: {doc.metadata.get('title')}")
    print(f"Page count: {doc.metadata.get('source', {}).get('page_count')}")
    
    # You can also provide custom metadata
    doc = pdf_to_mdp(
        pdf_data=sample_pdf,
        metadata={
            "title": "Custom PDF Title",
            "author": "Datapack User",
            "tags": ["pdf", "sample", "datapack"]
        }
    )
    print(f"Converted PDF with custom metadata to MDP document with ID: {doc.id}")

def main():
    """Run all converter examples."""
    print("Datapack Converter Examples")
    print("==========================")
    
    example_json_converter()
    example_xml_converter()
    example_csv_converter()
    example_yaml_converter()
    example_markdown_converter()
    example_pdf_converter()
    
    print("\nAll examples completed. Output files are in the './output' directory.")

if __name__ == "__main__":
    main() 