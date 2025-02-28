# Datapack Format Converters

This module provides tools for converting various file formats into MDP (Markdown Data Pack) files while preserving structure and metadata. These converters help you transform your existing data into the MDP format for use with Datapack's powerful document management and AI capabilities.

## Available Converters

The following converters are currently available:

- **JSON to MDP** - Convert JSON data to MDP format
- **XML to MDP** - Convert XML data to MDP format
- **CSV to MDP** - Convert CSV data to MDP format

## Usage

### JSON to MDP

Convert JSON data to an MDP document:

```python
from datapack.converters import json_to_mdp

# From a JSON file
doc = json_to_mdp("data.json", output_path="converted.mdp")

# From a JSON string
json_string = '{"title": "Example", "content": "This is an example"}'
doc = json_to_mdp(json_string)

# From a Python dictionary
json_dict = {"title": "Example", "content": "This is an example"}
doc = json_to_mdp(json_dict)

# With custom metadata
doc = json_to_mdp(
    "data.json",
    metadata={"title": "Custom Title", "tags": ["example", "json"]},
    extract_metadata=False  # Don't extract metadata from JSON
)
```

### XML to MDP

Convert XML data to an MDP document:

```python
from datapack.converters import xml_to_mdp

# From an XML file
doc = xml_to_mdp("data.xml", output_path="converted.mdp")

# From an XML string
xml_string = '<root><title>Example</title><content>This is an example</content></root>'
doc = xml_to_mdp(xml_string)

# With custom options
doc = xml_to_mdp(
    "data.xml",
    metadata={"title": "Custom Title", "tags": ["example", "xml"]},
    extract_metadata=False,  # Don't extract metadata from XML
    max_depth=3,  # Limit nesting depth
    include_attributes=True  # Include XML attributes
)
```

### CSV to MDP

Convert CSV data to an MDP document:

```python
from datapack.converters import csv_to_mdp

# From a CSV file
doc = csv_to_mdp("data.csv", output_path="converted.mdp")

# From a CSV string
csv_string = 'name,age,email\nJohn,30,john@example.com\nJane,25,jane@example.com'
doc = csv_to_mdp(csv_string)

# With custom options
doc = csv_to_mdp(
    "data.csv",
    metadata={"title": "Custom Title", "tags": ["example", "csv"]},
    extract_metadata=False,  # Don't extract metadata from CSV headers
    include_stats=True,      # Include summary statistics
    max_rows=50,             # Show only 50 rows
    delimiter=";",           # Use semicolon as delimiter
    has_header=True,         # First row is header
    encoding="utf-8"         # File encoding
)
```

## Extending Converters

You can extend the converters with your own custom logic:

```python
from datapack.converters import json_to_mdp
from mdp import Document

def my_custom_json_to_mdp(json_data, **kwargs):
    # Pre-process the JSON data
    # ...
    
    # Use the built-in converter
    doc = json_to_mdp(json_data, **kwargs)
    
    # Post-process the document
    doc.add_tag("processed-by-custom-converter")
    
    return doc
```

## Features

All converters provide the following features:

1. **Metadata Extraction** - Automatically extract metadata from the source format
2. **Custom Metadata** - Override or supplement extracted metadata
3. **Structured Content** - Convert the source format to well-structured Markdown
4. **Source Tracking** - Record the original source and conversion details
5. **Direct Integration** - Seamlessly integrate with Datapack's Document model

## Contributing

To add support for additional file formats, create a new converter module following the pattern of the existing converters. Each converter should:

1. Provide a main conversion function that returns an MDP Document
2. Extract metadata when possible
3. Convert the source format to structured Markdown
4. Include source information in the metadata

## Related Modules

- **mdp** - The core MDP file format library
- **datapack.ai** - AI-powered document processing
- **datapack.workflows** - Document workflow automation 