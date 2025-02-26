# Basic Usage

This guide covers the basic usage of Datapack, including how to work with documents, add metadata, and perform common operations.

## Getting Started with Documents

Datapack provides a unified interface for working with various document formats. Here's how to get started:

### Creating a Document

```python
from datapack import Document

# Create a document with content and metadata
doc = Document(
    content="# Example Document\n\nThis is an example document created with Datapack.",
    metadata={
        "title": "Example Document",
        "author": "Datapack User",
        "created_at": "2023-06-15",
        "tags": ["example", "documentation"]
    }
)

# Save the document as MDP (Datapack's native format)
doc.save("example.mdp")
```

### Loading Documents

```python
from datapack import Document

# Load from MDP format
doc = Document.from_file("example.mdp")

# Load from other formats
markdown_doc = Document.from_file("document.md")
pdf_doc = Document.from_file("document.pdf")  # Requires pdf extras
html_doc = Document.from_file("document.html")  # Requires html extras
docx_doc = Document.from_file("document.docx")  # Requires docx extras
```

### Accessing Document Content

```python
from datapack import Document

doc = Document.from_file("example.mdp")

# Access the full content
print(doc.content)

# Get document headings
headings = doc.get_headings()
for heading in headings:
    print(f"Level {heading.level}: {heading.text}")

# Get sections (heading + content)
sections = doc.get_sections()
for section in sections:
    print(f"Section: {section.title}")
    print(f"Content: {section.content[:100]}...")
```

## Working with Metadata

Datapack documents include rich metadata capabilities:

### Standard Metadata

```python
from datapack import Document

doc = Document.from_file("example.mdp")

# Access standard metadata
print(f"Title: {doc.metadata.title}")
print(f"Author: {doc.metadata.author}")
print(f"Created: {doc.metadata.created_at}")
print(f"Tags: {', '.join(doc.metadata.tags)}")

# Update metadata
doc.metadata.version = "1.1"
doc.metadata.updated_at = "2023-06-20"
doc.metadata.tags.append("updated")

# Save changes
doc.save("example_updated.mdp")
```

### Custom Metadata

```python
from datapack import Document

# Create a document with custom metadata
doc = Document(
    content="# Custom Metadata Example",
    metadata={
        "title": "Custom Metadata Example",
        "document_type": "tutorial",
        "complexity": "beginner",
        "estimated_reading_time": 5,
        "prerequisites": ["Datapack installation"],
        "related_documents": ["getting_started.mdp"]
    }
)

# Access custom metadata
print(f"Document Type: {doc.metadata.document_type}")
print(f"Complexity: {doc.metadata.complexity}")
print(f"Reading Time: {doc.metadata.estimated_reading_time} minutes")
```

## Converting Between Formats

Datapack allows easy conversion between document formats:

```python
from datapack import Document

# Load a document
doc = Document.from_file("example.mdp")

# Convert to different formats
doc.to_markdown("example.md")
doc.to_html("example.html")
doc.to_text("example.txt")
doc.to_json("example.json")
```

## Document Collections

For working with multiple documents:

```python
from datapack import DocumentCollection, Document

# Create a collection
collection = DocumentCollection("My Documents")

# Add documents to the collection
doc1 = Document.from_file("document1.mdp")
doc2 = Document.from_file("document2.mdp")

collection.add(doc1)
collection.add(doc2)

# Filter documents
tagged_docs = collection.filter(lambda doc: "important" in doc.metadata.tags)

# Perform operations on all documents
collection.process(lambda doc: doc.add_metadata(processed=True))

# Save all documents
collection.save_all(output_dir="./processed/")
```

## Next Steps

Once you're comfortable with these basics, you can:

- Explore [Advanced Features](advanced-features.md) for more complex operations
- Learn about [Security & Sharing](security-sharing.md) for collaborative workflows
- See the [Examples](../examples/index.md) section for practical use cases
- Check the [API Reference](../api/core.md) for detailed documentation 