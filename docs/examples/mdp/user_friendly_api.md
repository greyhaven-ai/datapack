# MDP User-Friendly API Examples

This document provides detailed examples of using the user-friendly API for working with MDP (Markdown Data Pack) files.

## Prerequisites

To run these examples, you'll need to have the `datapack` package installed:

```bash
pip install datapack
```

For advanced conversion examples, you may also need:

```bash
pip install pypdf requests beautifulsoup4
```

## Document Basics

These examples demonstrate how to create, save, load, and modify documents.

### Creating a Document

```python
from datapack.mdp import Document

# Create a new document with basic metadata
doc = Document.create(
    title="Getting Started with Datapack", 
    content="# Introduction\n\nThis document explains how to use Datapack.",
    author="Jane Doe"
)

# Adding additional metadata
doc.tags = ["tutorial", "datapack"]
doc.custom_field = "Custom value"

# Save the document
doc.save("getting_started.mdp")
```

### Loading a Document

```python
from datapack.mdp import Document

# Load a document from an MDP file
doc = Document.from_file("getting_started.mdp")

# Access metadata through properties
print(f"Title: {doc.title}")
print(f"Author: {doc.author}")
print(f"Tags: {doc.tags}")
print(f"Custom field: {doc.custom_field}")

# Access content
print(f"Content preview: {doc.content[:50]}...")
```

### Modifying a Document

```python
from datapack.mdp import Document

# Load a document
doc = Document.from_file("getting_started.mdp")

# Update metadata
doc.title = "Updated Title"
doc.add_tag("updated")

# Update content
doc.content = doc.content + "\n\n## New Section\n\nThis is a new section added to the document."

# Save the updated document
doc.save()
```

## Document Relationships

These examples demonstrate how to create and manage relationships between documents.

### Creating Parent-Child Relationships

```python
from datapack.mdp import Document

# Create parent document
parent_doc = Document.create(
    title="Parent Document",
    content="This is the parent document."
)
parent_doc.save("parent.mdp")

# Create child document with a relationship to the parent
child_doc = Document.create(
    title="Child Document",
    content="This is a child document."
)

# Add relationship to parent
child_doc.add_relationship("parent.mdp", relationship_type="child_of")
child_doc.save("child.mdp")
```

### Retrieving Related Documents

```python
from datapack.mdp import Document

# Load a document
doc = Document.from_file("parent.mdp")

# Get all related documents
related_docs = doc.get_related_documents()
print(f"Found {len(related_docs)} related documents")

# Get documents with a specific relationship type
child_docs = doc.get_related_documents(relationship_type="child_of")
for child in child_docs:
    print(f"Child document: {child.title}")
```

## Document Collections

These examples demonstrate how to create and manage collections of documents.

### Creating a Collection

```python
from datapack.mdp import Document, Collection

# Create some documents
doc1 = Document.create(title="Document 1", content="Content 1")
doc2 = Document.create(title="Document 2", content="Content 2")
doc3 = Document.create(title="Document 3", content="Content 3")

# Create a collection and add documents
collection = Collection("My Collection")
collection.add_documents([doc1, doc2, doc3])

# Save all documents in the collection
collection.save_all("collection_dir")
```

### Loading a Collection from a Directory

```python
from datapack.mdp import Collection

# Load collection from a directory
collection = Collection.from_directory("collection_dir", name="My Collection")

# Access documents in the collection
print(f"Collection: {collection.name}")
print(f"Number of documents: {len(collection.documents)}")

# Find a document by title
doc = collection.get_document_by_title("Document 1")
if doc:
    print(f"Found document: {doc.title}")
```

### Filtering Documents in a Collection

```python
from datapack.mdp import Collection

# Load collection
collection = Collection.from_directory("collection_dir")

# Filter documents that contain a specific tag
tagged_docs = collection.filter(lambda doc: "tutorial" in doc.tags)
print(f"Found {len(tagged_docs)} documents with 'tutorial' tag")

# Filter documents by content
content_docs = collection.filter(lambda doc: "important" in doc.content.lower())
print(f"Found {len(content_docs)} documents containing 'important'")
```

### Exporting a Collection

```python
from datapack.mdp import Collection

# Load collection
collection = Collection.from_directory("collection_dir")

# Export the collection to another directory
# This creates an index file and copies all documents
collection.export("exported_collection")
```

## File Conversion

These examples demonstrate how to convert various file types to MDP format.

### Converting a Single File

```python
from datapack.mdp import convert_file

# Convert a Markdown file to MDP
mdp_doc = convert_file(
    "example.md", 
    output_path="example.mdp",
    title="Converted Markdown"
)

# Add additional metadata after conversion
mdp_doc.author = "John Smith"
mdp_doc.tags = ["converted", "markdown"]
mdp_doc.save()
```

### Converting a Directory of Files

```python
from datapack.mdp import convert_directory

# Convert all Markdown and text files in a directory
converted_docs = convert_directory(
    "documents/", 
    output_directory="mdp_documents/",
    file_patterns=["*.md", "*.txt"],
    add_metadata={"source": "bulk_conversion"}
)

print(f"Converted {len(converted_docs)} documents")
```

## Advanced Conversions

These examples demonstrate more advanced conversion features.

### Extracting Text from PDFs

```python
from datapack.mdp import extract_text_from_pdf

# Extract text from a PDF and convert to MDP
pdf_doc = extract_text_from_pdf(
    "document.pdf",
    output_path="document.mdp",
    title="Extracted PDF Content"
)

print(f"Extracted content from PDF to {pdf_doc.path}")
```

### Importing Content from Websites

```python
from datapack.mdp import import_website

# Import content from a website
web_doc = import_website(
    "https://example.com/article",
    output_path="web_content.mdp",
    title="Imported Web Content"
)

print(f"Imported web content to {web_doc.path}")
```

## Backward Compatibility

These examples demonstrate how the new API maintains backward compatibility with the original API.

### Working with Both APIs

```python
# Using the original API
from datapack.mdp.core import read_mdp, write_mdp
from datapack.mdp.metadata import create_metadata

# Create a document with the original API
metadata = create_metadata(title="Original API Document")
mdp_file = write_mdp("original.mdp", metadata, "# Content created with the original API")

# Now use the user-friendly API with the same document
from datapack.mdp import Document

# Load the document with the user-friendly API
doc = Document.from_file("original.mdp")
print(f"Loaded with user-friendly API: {doc.title}")

# Modify with the user-friendly API
doc.add_tag("mixed_api_example")
doc.save()

# Read it again with the original API
mdp_file = read_mdp("original.mdp")
print(f"Read with original API: {mdp_file.metadata['title']}")
print(f"Tags: {mdp_file.metadata.get('tags', [])}")
```

## Running the Examples

You can find a runnable Python script with all these examples in the repository at `docs/examples/mdp/user_friendly_api.py`.

To run the examples:

```bash
cd docs/examples/mdp
python user_friendly_api.py
```

## See Also

- [MDP API Reference](../../api/mdp.md)
- [MDP Format Documentation](../../mdp_format.md)
- [Quick Start Guide](../../quick-start.md) 