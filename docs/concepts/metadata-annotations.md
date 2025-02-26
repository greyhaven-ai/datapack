# Metadata & Annotations

This guide explores two key concepts in Datapack: metadata and annotations. Both serve to enrich documents with additional information, but they do so in different ways and for different purposes.

## Metadata

Metadata is structured information about a document that describes its properties, characteristics, and context. It provides a way to categorize, organize, and understand documents without needing to analyze their content.

### Types of Metadata in Datapack

1. **Standard Metadata**: Predefined fields that provide consistent information across documents
   - Title, author, creation date, version, etc.
   - See [Standard Metadata](../examples/metadata/standard-metadata.md) for details

2. **Custom Metadata**: User-defined fields specific to particular use cases
   - Domain-specific properties
   - Application-specific attributes
   - See [Custom Metadata](../examples/metadata/custom-metadata.md) for examples

3. **System Metadata**: Automatically generated or managed by Datapack
   - File paths, identifiers, processing history, etc.

### Working with Metadata

Metadata in Datapack is typically stored in the YAML frontmatter section of MDP files:

```yaml
---
title: Example Document
author: John Doe
version: 1.0.0
created_at: 2023-05-15
tags:
  - example
  - documentation
custom_property: custom value
---
```

Programmatically, metadata can be accessed and modified through the `metadata` property of document objects:

```python
from datapack import Document

# Create a document with metadata
doc = Document(
    content="# Example",
    metadata={
        "title": "Example Document",
        "author": "John Doe"
    }
)

# Access metadata
print(doc.metadata.title)  # "Example Document"

# Modify metadata
doc.metadata.version = "1.0.0"
doc.metadata.tags = ["draft", "internal"]
```

## Annotations

Annotations are a way to add information to specific parts of a document's content. Unlike metadata (which applies to the entire document), annotations mark up, classify, or add context to particular sections, ranges, or elements within the document.

### Types of Annotations

1. **Span Annotations**: Apply to a specific range of text
   - Examples: highlights, comments, semantic classifications

2. **Element Annotations**: Apply to structural elements like headings, paragraphs, or lists
   - Examples: section classifications, importance ratings

3. **Relational Annotations**: Establish connections between different parts of a document
   - Examples: cross-references, semantic relationships

### Annotation Structure

A typical annotation includes:

- **Range**: Where in the document the annotation applies (start/end positions)
- **Type**: What kind of annotation it is (e.g., "comment", "highlight", "classification")
- **Metadata**: Additional information about the annotation
- **Creator**: Who created the annotation (optional)
- **Timestamp**: When the annotation was created (optional)

### Working with Annotations

```python
from datapack import Document, Annotation

# Create a document
doc = Document(content="# Introduction\n\nThis is an example document.")

# Add a span annotation
doc.add_annotation(
    Annotation(
        start=0,  # Position in the document content
        end=13,   # End position
        type="heading",
        metadata={"level": 1}
    )
)

# Add another annotation
doc.add_annotation(
    Annotation(
        start=15,
        end=43,
        type="paragraph",
        metadata={"sentiment": "neutral"}
    )
)

# Access annotations
for annotation in doc.annotations:
    print(f"Type: {annotation.type}")
    print(f"Range: {annotation.start}-{annotation.end}")
    print(f"Text: {doc.content[annotation.start:annotation.end]}")
    print(f"Metadata: {annotation.metadata}")
```

## Benefits of Metadata and Annotations

### Metadata Benefits

1. **Organization**: Facilitates document categorization and filtering
2. **Discoverability**: Makes documents easier to find and identify
3. **Processing**: Enables automated processing based on document properties
4. **Integration**: Supports interoperability with other systems

### Annotation Benefits

1. **Context**: Adds contextual information to specific content
2. **Analysis**: Enables detailed content analysis and interpretation
3. **Collaboration**: Supports comments and collaborative markup
4. **Processing**: Allows targeted processing of specific document parts

## Best Practices

1. **Consistent Schema**: Develop and maintain a consistent metadata schema
2. **Minimal Required Fields**: Define a minimal set of required metadata fields
3. **Validation**: Validate metadata and annotations against defined schemas
4. **Automation**: Automate metadata and annotation creation when possible
5. **Documentation**: Document your metadata schema and annotation types

## Next Steps

- Learn about [Context & Relationships](context-relationships.md)
- Explore [Standard Metadata Examples](../examples/metadata/standard-metadata.md)
- See [Custom Metadata Examples](../examples/metadata/custom-metadata.md)
- Discover how to use [Annotations in Practice](../examples/context/adding-context.md) 