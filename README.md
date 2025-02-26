# Datapack

Datapack is a powerful platform for document ingestion, parsing, annotation, and secure sharing across software ecosystems. It provides a comprehensive set of tools for working with various document types and integrating with Large Language Models (LLMs).

## Key Features

- **Document Processing**: Ingest and parse documents in multiple formats (PDF, Word, CSV, JSON, XML, Markdown, HTML, MDP)
- **Metadata & Annotations**: Add rich metadata and annotations to documents
- **Context-Aware**: Build and maintain relationships between documents and their contexts
- **Secure Sharing**: Share documents securely across different software systems
- **LLM Integration**: Seamlessly integrate with powerful language models
- **User-Friendly API**: Work with documents easily using our intuitive high-level API

## Installation

```bash
# Basic installation
pip install datapack

# With PDF support
pip install datapack[pdf]

# For development
pip install datapack[dev]
```

## Quick Start

### Working with MDP Documents

The Markdown Data Package (MDP) format is Datapack's native document format. It combines the readability of Markdown with structured metadata capabilities.

```python
from datapack.mdp import Document

# Create a new document
doc = Document.create(
    title="My First Document",
    content="# Hello World\n\nThis is my first MDP document.",
    author="John Doe",
    tags=["example", "tutorial"]
)

# Save to an MDP file
doc.save("my_document.mdp")

# Load from an MDP file
loaded_doc = Document.from_file("my_document.mdp")

# Access properties
print(loaded_doc.title)  # "My First Document"
print(loaded_doc.author)  # "John Doe"
print(loaded_doc.tags)    # ["example", "tutorial"]

# Update properties
loaded_doc.title = "Updated Title"
loaded_doc.add_tag("updated")

# Save changes
loaded_doc.save()
```

### Working with Document Collections

```python
from datapack.mdp import Collection, Document

# Create a collection
collection = Collection("My Collection")

# Add documents
doc1 = Document.create(title="First Document", content="# First Document")
doc2 = Document.create(title="Second Document", content="# Second Document")

collection.add_document(doc1)
collection.add_document(doc2)

# Create relationships between documents
doc1.add_relationship(doc2, relationship_type="related")

# Save all documents in a collection
collection.save_all("documents/")

# Load a collection from a directory
loaded_collection = Collection.from_directory("documents/")
```

### New Feature: Automatic Metadata Extraction

Datapack now includes functionality to automatically extract metadata from document content:

```python
from datapack.mdp import Document

# Create document with automatically extracted metadata
doc = Document.create_with_auto_metadata(
    content="""# Machine Learning Basics
    
    This document covers the fundamentals of machine learning,
    including supervised learning, neural networks, and model evaluation.
    """
)

# The metadata will be automatically extracted:
print(doc.title)  # "Machine Learning Basics"
print(doc.tags)   # ["machine", "learning", "neural", "networks", "model"]

# You can also enhance existing documents
existing_doc = Document.create(title="My Document")
existing_doc.content = "# Document Content\n\nThis is about programming and data science."
existing_doc.auto_enhance_metadata()
```

### Command-Line Interface

Datapack includes a CLI for common tasks:

```bash
# Create a new MDP document
datapack create --title "My Document" --output document.mdp

# Generate API documentation
datapack generate-api-docs --code-dir ./src --output api_docs.mdp --module-name "MyModule"

# Synchronize code documentation
datapack sync-docs --code-dir ./src --docs-dir ./docs

# Create release notes
datapack release-notes --version "1.0.0" --project "MyProject" --output release_notes.mdp --changes '[ 
  {"type": "feat", "description": "Added new feature"},
  {"type": "fix", "description": "Fixed bug"}
]'
```

## Understanding MDP Format

An MDP file consists of two main components:

1. **YAML Frontmatter**: Structured metadata at the beginning of the file
2. **Markdown Content**: The document's content in Markdown format

Example:

```markdown
---
title: Example Document
author: John Doe
version: 1.0.0
created_at: 2023-06-01
tags:
  - example
  - documentation
---

# Example Document

This is the content of the document written in Markdown.

## Section 1

This is a section with **formatting** and [links](https://example.com).
```

## Developer Workflows

Datapack provides tools for integrating with development workflows:

```python
from datapack.mdp.workflows import (
    sync_codebase_docs,
    generate_api_docs,
    create_release_notes
)

# Generate documentation from code comments
docs = sync_codebase_docs(
    code_directory="./src",
    docs_directory="./docs",
    file_patterns=["*.py", "*.js"]
)

# Create API reference
api_doc = generate_api_docs(
    code_directory="./src",
    output_file="./docs/api_reference.mdp",
    module_name="MyModule"
)

# Generate release notes
release_doc = create_release_notes(
    version="1.0.0",
    output_file="./docs/release_notes.mdp",
    changes=[
        {"type": "feat", "description": "Added new feature X"},
        {"type": "fix", "description": "Fixed critical bug Y"}
    ],
    project_name="MyProject"
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

License Disclaimer

This project is primarily licensed under the GNU Affero General Public License v3.0 (AGPL-3.0), as specified in the LICENSE file in the root directory of this repository. However, certain components of this project are licensed under the MIT License. Refer to the LICENSE files in these specific directories for details.

Please note:

The AGPL-3.0 license applies to all parts of the project unless otherwise specified.
The SDKs and MDP file format are licensed under the MIT License. Refer to the LICENSE files in these specific directories for details.
When using or contributing to this project, ensure you comply with the appropriate license terms for the specific component you are working with.
For more details on the licensing of specific components, please refer to the LICENSE files in the respective directories or contact the project maintainers.
