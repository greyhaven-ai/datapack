# Simple Document Example

This example demonstrates how to create, read, and work with a basic document in Datapack.

## Creating a Simple Document

The following code creates a basic document with content and metadata:

```python
from datapack import Document

# Create a document with content and basic metadata
doc = Document(
    content="""# Sample Document

This is a simple document created with Datapack.

## Introduction

Datapack makes it easy to create and work with documents.

## Features

- Simple API
- Metadata support
- Markdown-based
- Easy to use
""",
    metadata={
        "title": "Sample Document",
        "author": "Datapack User",
        "version": "1.0.0",
        "created_at": "2023-06-01",
        "tags": ["example", "basic"]
    }
)

# Save the document as an MDP file
doc.save("sample_document.mdp")
```

This creates a document with markdown content and several metadata fields, then saves it as an MDP file.

## Examining the MDP File

The generated MDP file looks like this:

```markdown
---
title: Sample Document
author: Datapack User
version: 1.0.0
created_at: '2023-06-01'
tags:
- example
- basic
---

# Sample Document

This is a simple document created with Datapack.

## Introduction

Datapack makes it easy to create and work with documents.

## Features

- Simple API
- Metadata support
- Markdown-based
- Easy to use
```

As you can see, an MDP file consists of:

1. YAML frontmatter between triple-dash (`---`) delimiters containing metadata
2. Markdown content after the frontmatter

## Reading a Document

Now let's read the document we created:

```python
from datapack import Document

# Load the document from file
doc = Document.from_file("sample_document.mdp")

# Access content
print("Document Content:")
print(doc.content)

# Access metadata
print("\nDocument Metadata:")
print(f"Title: {doc.metadata.title}")
print(f"Author: {doc.metadata.author}")
print(f"Version: {doc.metadata.version}")
print(f"Created at: {doc.metadata.created_at}")
print(f"Tags: {', '.join(doc.metadata.tags)}")
```

The output will look something like this:

```
Document Content:
# Sample Document

This is a simple document created with Datapack.

## Introduction

Datapack makes it easy to create and work with documents.

## Features

- Simple API
- Metadata support
- Markdown-based
- Easy to use

Document Metadata:
Title: Sample Document
Author: Datapack User
Version: 1.0.0
Created at: 2023-06-01
Tags: example, basic
```

## Modifying a Document

Let's modify the document by adding a new section and updating some metadata:

```python
from datapack import Document

# Load the document
doc = Document.from_file("sample_document.mdp")

# Add a new section to the content
doc.content += """
## Benefits

Using Datapack provides several benefits:

1. Simplified document management
2. Structured metadata
3. Easy integration with other systems
"""

# Update metadata
doc.metadata.version = "1.1.0"
doc.metadata.updated_at = "2023-06-02"
doc.metadata.tags.append("updated")

# Save the updated document
doc.save("updated_document.mdp")
```

## Working with Document Structure

Datapack provides tools to work with document structure:

```python
from datapack import Document

# Load the document
doc = Document.from_file("updated_document.mdp")

# Get headings
headings = doc.get_headings()
print("Document Headings:")
for heading in headings:
    print(f"- {heading.level} {heading.text}")

# Get sections (heading + content)
sections = doc.get_sections()
print("\nDocument Sections:")
for section in sections:
    print(f"Section: {section.title}")
    print(f"Content length: {len(section.content)} characters")
```

The output would look like:

```
Document Headings:
- 1 Sample Document
- 2 Introduction
- 2 Features
- 2 Benefits

Document Sections:
Section: Sample Document
Content length: 42 characters
Section: Introduction
Content length: 56 characters
Section: Features
Content length: 63 characters
Section: Benefits
Content length: 116 characters
```

## Complete Example

Here's a complete script that demonstrates all of these operations:

```python
from datapack import Document

# Create a document
print("Creating document...")
doc = Document(
    content="""# Sample Document

This is a simple document created with Datapack.

## Introduction

Datapack makes it easy to create and work with documents.

## Features

- Simple API
- Metadata support
- Markdown-based
- Easy to use
""",
    metadata={
        "title": "Sample Document",
        "author": "Datapack User",
        "version": "1.0.0",
        "created_at": "2023-06-01",
        "tags": ["example", "basic"]
    }
)
doc.save("sample_document.mdp")
print("Document created and saved.")

# Read the document
print("\nReading document...")
loaded_doc = Document.from_file("sample_document.mdp")
print(f"Title: {loaded_doc.metadata.title}")
print(f"Author: {loaded_doc.metadata.author}")
print(f"Content length: {len(loaded_doc.content)} characters")

# Modify the document
print("\nModifying document...")
loaded_doc.content += """
## Benefits

Using Datapack provides several benefits:

1. Simplified document management
2. Structured metadata
3. Easy integration with other systems
"""
loaded_doc.metadata.version = "1.1.0"
loaded_doc.metadata.updated_at = "2023-06-02"
loaded_doc.save("updated_document.mdp")
print("Document updated and saved.")

# Analyze document structure
print("\nAnalyzing document structure...")
headings = loaded_doc.get_headings()
print(f"Number of headings: {len(headings)}")
sections = loaded_doc.get_sections()
print(f"Number of sections: {len(sections)}")
```

## Next Steps

Now that you've learned how to create and work with simple documents, you can explore:

- [Document Parsing](document-parsing.md): Learn how to parse different document formats
- [Standard Metadata](../metadata/standard-metadata.md): Discover standard metadata fields
- [Adding Context](../context/adding-context.md): Learn to add context to your documents 