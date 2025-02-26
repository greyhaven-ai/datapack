# MDP API Reference

This document provides a comprehensive reference for the Markdown Data Pack (MDP) module's API.

## Overview

The MDP module provides functionality for working with MDP files, which are Markdown files with YAML frontmatter metadata. The module offers two API levels:

1. A user-friendly high-level API centered around the `Document` and `Collection` classes
2. A lower-level core API for direct manipulation of MDP files

## User-Friendly API

### Document Class

```python
from datapack.mdp import Document
```

The `Document` class represents an MDP file with convenient property accessors and methods.

#### Class Methods

| Method | Description |
|--------|-------------|
| `Document.create(title, content="", author=None, **metadata_kwargs)` | Create a new document with the given metadata |
| `Document.from_file(path)` | Load a document from an MDP file |

#### Instance Methods

| Method | Description |
|--------|-------------|
| `save(path=None)` | Save the document to a file |
| `to_string()` | Convert the document to its string representation |
| `add_tag(tag)` | Add a tag to the document |
| `remove_tag(tag)` | Remove a tag from the document |
| `add_relationship(target, relationship_type="related", title=None, description=None)` | Add a relationship to another document |
| `get_related_documents(relationship_type=None, base_path=None)` | Get related documents |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `content` | str | The Markdown content of the document |
| `metadata` | dict | The metadata dictionary of the document |
| `path` | Path | The path to the document file (if saved) |
| `title` | str | The document title |
| `author` | str | The document author |
| `created_at` | str | The document creation date |
| `updated_at` | str | The document last update date |
| `tags` | list | The document tags |

### Collection Class

```python
from datapack.mdp import Collection
```

The `Collection` class manages groups of related documents.

#### Class Methods

| Method | Description |
|--------|-------------|
| `Collection.from_directory(directory, name=None, recursive=True, file_pattern="*.mdp")` | Create a collection from documents in a directory |

#### Instance Methods

| Method | Description |
|--------|-------------|
| `add_document(document)` | Add a document to the collection |
| `add_documents(documents)` | Add multiple documents to the collection |
| `remove_document(document)` | Remove a document from the collection |
| `get_document_by_title(title)` | Find a document by title |
| `get_document_by_uuid(uuid_str)` | Find a document by UUID |
| `filter(predicate)` | Filter documents using a predicate function |
| `get_hierarchy()` | Get the parent-child hierarchy of documents |
| `link_documents_by_references()` | Create relationships based on content references |
| `save_all(directory=None)` | Save all documents in the collection |
| `export(directory)` | Export the collection to a directory with an index |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | The name of the collection |
| `documents` | list | The list of documents in the collection |
| `metadata` | dict | The metadata dictionary of the collection |

## Conversion Utilities

### File Conversion Functions

```python
from datapack.mdp import convert_file, convert_directory
```

These functions provide easy conversion of various file types to MDP documents.

#### Functions

| Function | Description |
|----------|-------------|
| `convert_file(file_path, output_path=None, title=None, add_metadata=None)` | Convert a file to an MDP document |
| `convert_directory(directory, output_directory=None, recursive=True, file_patterns=["*.txt", "*.md", "*.markdown"], add_metadata=None)` | Convert all matching files in a directory to MDP documents |
| `extract_text_from_pdf(pdf_path, output_path=None, title=None)` | Extract text from a PDF and convert it to an MDP document |
| `import_website(url, output_path=None, title=None)` | Import content from a website and convert it to an MDP document |

## Core API

### Low-Level MDP Functions

```python
from datapack.mdp.core import MDPFile, read_mdp, write_mdp
```

These functions provide direct access to MDP file manipulation.

#### Functions

| Function | Description |
|----------|-------------|
| `read_mdp(path)` | Read an MDP file and return an MDPFile object |
| `write_mdp(path, metadata, content)` | Write an MDP file and return an MDPFile object |

### Metadata Functions

```python
from datapack.mdp.metadata import create_metadata, validate_metadata
```

These functions help with metadata creation and validation.

#### Functions

| Function | Description |
|----------|-------------|
| `create_metadata(title="Untitled Document", author=None, **kwargs)` | Create a metadata dictionary with sensible defaults |
| `validate_metadata(metadata)` | Validate a metadata dictionary against the schema |
| `generate_uuid()` | Generate a unique identifier for a document |
| `is_valid_uuid(uuid_str)` | Check if a string is a valid UUID |
| `create_uri(doc_id, namespace=None)` | Create a URI for a document |
| `parse_uri(uri)` | Parse a document URI into its components |
| `create_relationship(reference, relationship_type, title=None, description=None, is_uri=False)` | Create a relationship dictionary |
| `add_relationship_to_metadata(metadata, relationship)` | Add a relationship to metadata |
| `create_collection_metadata(name, collection_id, description=None)` | Create metadata for a collection |

### Utility Functions

```python
from datapack.mdp.utils import find_mdp_files, resolve_reference, find_related_documents
```

These utility functions help with common MDP operations.

#### Functions

| Function | Description |
|----------|-------------|
| `find_mdp_files(directory, recursive=True, pattern="*.mdp")` | Find all MDP files in a directory |
| `resolve_reference(reference, base_path=None)` | Resolve a reference to a document |
| `find_related_documents(mdp_file, relationship_type=None, base_path=None)` | Find documents related to an MDPFile |
| `find_collection_members(collection_id, directory, recursive=True)` | Find members of a collection |
| `get_collection_hierarchy(mdp_files)` | Get the parent-child hierarchy of a collection |
| `convert_to_mdp(file_path, output_path=None, metadata=None)` | Convert a file to an MDP file |
| `batch_convert_to_mdp(file_paths, output_dir=None, metadata=None)` | Convert multiple files to MDP files |

## Examples

For detailed examples of how to use these APIs, see the [User-Friendly MDP API Examples](../examples/mdp/user_friendly_api.md).

## See Also

- [MDP Format Documentation](../mdp_format.md)
- [Quick Start Guide](../quick-start.md) 