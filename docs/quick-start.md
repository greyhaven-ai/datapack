# Quick Start Guide

This guide will help you get started with Datapack quickly, demonstrating the basic functionality and workflow.

## Prerequisites

Before you begin, make sure you have:

- Python 3.8 or higher installed
- Datapack [installed](installation.md) on your system
- Basic familiarity with Python

## Basic Usage Example

Let's walk through a simple example to demonstrate Datapack's core functionality.

### 1. Create a Simple Document

First, let's create a simple document using Datapack's MDP module:

```python
from mdp import Document

# Create a new document with content and metadata
doc = Document.create(
    title="Sample Document",
    content="# Sample Document\n\nThis is a sample document created with Datapack.",
    author="Datapack User",
    tags=["sample", "quickstart"]
)

# Save the document as an MDP file
doc.save("sample_document.mdp")

print(f"Document created and saved to sample_document.mdp")
```

This code creates a new document with markdown content and some basic metadata, then saves it as an MDP file.

### 2. Read and Access a Document

Now, let's read the document and access its contents and metadata:

```python
from mdp import Document

# Load the document from file
doc = Document.from_file("sample_document.mdp")

# Access content
print("Document Content:")
print(doc.content)

# Access metadata using property accessors
print("\nDocument Metadata:")
print(f"Title: {doc.title}")
print(f"Author: {doc.author}")
print(f"Tags: {', '.join(doc.tags)}")
```

### 3. Modify a Document

Let's update the document with new content and metadata:

```python
from mdp import Document

# Load the document
doc = Document.from_file("sample_document.mdp")

# Update content
doc.content += "\n\n## New Section\n\nThis section was added to demonstrate document modification."

# Update metadata using property accessors
doc.updated_at = "2023-06-01"
doc.add_tag("updated")

# Save the updated document
doc.save("updated_document.mdp")

print("Document updated and saved to updated_document.mdp")
```

### 4. Working with Document Collections

Datapack's MDP module allows you to work with collections of documents:

```python
from mdp import Document, Collection
import os

# Create a collection
collection = Collection("Documentation Collection")

# Create a few documents
for i in range(1, 4):
    doc = Document.create(
        title=f"Document {i}",
        content=f"# Document {i}\n\nThis is document {i} in the collection.",
        tags=["documentation", f"doc-{i}"]
    )
    collection.add_document(doc)

# Save the collection to a directory
os.makedirs("collection", exist_ok=True)
collection.save_all("collection")

# Load the collection from the directory
loaded_collection = Collection.from_directory("collection")
print(f"Loaded collection with {len(loaded_collection)} documents")

# Filter documents by tag
filtered_docs = loaded_collection.filter(lambda doc: "doc-2" in doc.tags)
print(f"Found {len(filtered_docs)} documents with tag 'doc-2'")
```

### 5. Establish Document Relationships

Datapack allows you to establish relationships between documents:

```python
from mdp import Document

# Create two documents
parent_doc = Document.create(
    title="Primary Document",
    content="# Primary Document\n\nThis is the primary document."
)

child_doc = Document.create(
    title="Child Document",
    content="# Child Document\n\nThis is a child document."
)

# Save the documents
parent_doc.save("primary.mdp")
child_doc.save("child.mdp")

# Add a relationship from the child to the parent
child_doc.add_relationship(
    parent_doc, 
    relationship_type="parent",
    description="This document extends the primary document"
)

# Save the updated child document
child_doc.save()

# Load the child document and get related documents
loaded_child = Document.from_file("child.mdp")
related_docs = loaded_child.get_related_documents()

print(f"Found {len(related_docs)} related documents")
for doc in related_docs:
    print(f"- {doc.title}")
```

### 6. Converting Files to MDP Format

Datapack provides utility functions for converting various file formats to MDP:

```python
from mdp import convert_file, convert_directory

# Convert a single file
doc = convert_file(
    "document.txt", 
    title="Converted Text Document",
    add_metadata={"status": "draft"}
)

# Convert all files in a directory
docs = convert_directory(
    "source_documents/",
    output_directory="converted/",
    recursive=True,
    file_patterns=["*.txt", "*.md"]
)

print(f"Converted {len(docs)} documents")
```

## Next Steps

Now that you've learned the basics of Datapack, you can:

- Explore more [examples](examples/index.md)
- Learn about the [MDP format](mdp_format.md) in detail
- Check the full [API reference](api/index.md)
- Read the [user guide](user-guide/index.md) for more detailed information 