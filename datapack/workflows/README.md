# Datapack Workflows

This directory contains high-level workflows for common operations in Datapack.

## Contents

- **Content Workflows**: Document creation and processing operations
- **Release Workflows**: Version and release management
- **Development Workflows**: Utilities for package development
- **AI Processing Workflows**: AI-powered document processing workflows

## AI Processing Workflows

The AI processing workflows combine PydanticAI-powered agents to provide comprehensive document processing capabilities:

### Features

- **Dependency Injection System**: Provides context-specific data for AI agents
- **Document Processing**: Extract metadata, key insights, and more from documents
- **Collection Processing**: Process collections of related documents
- **Relationship Extraction**: Identify and manage relationships between documents
- **Content Enhancement**: Improve document content with AI-powered editing
- **File Conversion**: Convert various file formats to MDP format
- **Agent-Based Workflows**: Combine specialized agents for complex tasks

### Basic Usage

```python
from datapack.workflows import process_document, process_documents, ai_convert_directory

# Process a single document
processed_doc = process_document(
    document="example.md",
    extract_metadata=True,
    extract_insights=True,
    enhance_content=True
)

# Process a collection of documents
from mdp import Collection
collection = Collection(name="My Collection", documents=[...])
processed_collection = process_documents(
    collection=collection,
    extract_relationships=True,
    max_concurrent=3
)

# Convert and process files in a directory
documents, collection = ai_convert_directory(
    source_directory="source",
    output_directory="output",
    file_pattern="*.{md,txt,pdf}",
    recursive=True
)
```

### Advanced Usage

For more advanced usage including custom processing pipelines, see `examples.py` which demonstrates:

- Custom document processing pipelines
- Using multiple agents with different configurations
- Working with asynchronous workflows
- Integration with PydanticAI agents and RunContext

## Content Workflows

The content workflows provide utilities for creating and managing document content:

- **Document Creation**: Templates for creating new documents
- **Package Creation**: Utilities for creating new packages
- **Document Conversion**: Tools for converting between formats

## Release Workflows

The release workflows handle version management and release processes:

- **Version Management**: Utilities for managing version numbers
- **Changelog Generation**: Tools for generating changelogs
- **Release Validation**: Tools for validating releases

## Usage Examples

See `examples.py` for detailed usage examples of all workflows. 