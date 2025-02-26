# Advanced Features

This guide covers the more advanced features of Datapack, allowing you to leverage its full capabilities for complex document processing scenarios.

## Document Annotations

Annotations provide a way to add context to specific parts of a document:

```python
from datapack import Document, Annotation

# Load or create a document
doc = Document.from_file("example.mdp")

# Add a highlight annotation
doc.add_annotation(
    Annotation(
        start=0,  # Start position in the content
        end=20,   # End position in the content
        type="highlight",
        metadata={
            "color": "yellow",
            "importance": "high",
            "author": "Alice"
        }
    )
)

# Add a comment annotation
doc.add_annotation(
    Annotation(
        start=100,
        end=150,
        type="comment",
        metadata={
            "text": "This section needs clarification",
            "author": "Bob",
            "created_at": "2023-06-15T10:30:00Z"
        }
    )
)

# Save the annotated document
doc.save("annotated_document.mdp")
```

### Working with Annotations

```python
from datapack import Document

# Load an annotated document
doc = Document.from_file("annotated_document.mdp")

# Get all annotations
annotations = doc.annotations
print(f"Document has {len(annotations)} annotations")

# Filter annotations by type
highlights = doc.get_annotations(type="highlight")
comments = doc.get_annotations(type="comment")

# Get annotations by author
alice_annotations = doc.get_annotations(filter_func=lambda a: a.metadata.get("author") == "Alice")

# Get text snippets for annotations
for annotation in annotations:
    text = doc.content[annotation.start:annotation.end]
    print(f"{annotation.type}: {text}")
    print(f"Metadata: {annotation.metadata}")
```

## Document Relationships

Datapack allows you to establish relationships between documents:

```python
from datapack import Document, Relationship

# Load documents
doc1 = Document.from_file("document1.mdp")
doc2 = Document.from_file("document2.mdp")

# Create a relationship
doc1.add_relationship(
    Relationship(
        target="document2.mdp",  # Target document path or ID
        type="references",       # Relationship type
        metadata={
            "context": "Chapter 3 references the API documentation",
            "importance": "high"
        }
    )
)

# Create a reverse relationship
doc2.add_relationship(
    Relationship(
        target="document1.mdp",
        type="referenced_by",
        metadata={
            "context": "API documentation referenced by the guide"
        }
    )
)

# Save documents with relationships
doc1.save("document1.mdp")
doc2.save("document2.mdp")
```

### Navigating Relationships

```python
from datapack import Document, DocumentResolver

# Load a document with relationships
doc = Document.from_file("document1.mdp")

# Get all relationships
relationships = doc.relationships
print(f"Document has {len(relationships)} relationships")

# Filter relationships by type
references = doc.get_relationships(type="references")
referenced_by = doc.get_relationships(type="referenced_by")

# Resolve related documents
resolver = DocumentResolver(base_path="./documents/")
for relationship in references:
    related_doc = resolver.resolve(relationship.target)
    print(f"Related document: {related_doc.metadata.title}")
```

## Advanced Document Processing

### Content Extraction and Analysis

```python
from datapack import Document, ContentAnalyzer

# Load a document
doc = Document.from_file("document.mdp")

# Extract different content elements
headings = doc.get_headings()
code_blocks = doc.get_elements("code")
tables = doc.get_elements("table")
links = doc.get_elements("link")
images = doc.get_elements("image")

# Analyze content structure
analyzer = ContentAnalyzer()
analysis = analyzer.analyze(doc)

# Get content statistics
stats = analysis.statistics
print(f"Word count: {stats.word_count}")
print(f"Reading time: {stats.reading_time} minutes")
print(f"Complexity score: {stats.complexity_score}")

# Get content breakdown
breakdown = analysis.breakdown
print(f"Paragraphs: {breakdown.paragraph_count}")
print(f"Lists: {breakdown.list_count}")
print(f"Tables: {breakdown.table_count}")
print(f"Code blocks: {breakdown.code_block_count}")
```

### Document Transformation

```python
from datapack import Document, Transformer

# Load a document
doc = Document.from_file("document.mdp")

# Create a transformer
transformer = Transformer()

# Apply transformations
transformer.add_heading_numbers(doc)  # Add numbers to headings (1, 1.1, 1.1.1)
transformer.fix_internal_links(doc)   # Update internal link references
transformer.normalize_metadata(doc)   # Normalize metadata fields
transformer.extract_toc(doc)          # Extract table of contents

# Custom transformation function
def convert_lists_to_tables(doc):
    # Implementation of custom transformation
    pass

transformer.apply(doc, convert_lists_to_tables)

# Save the transformed document
doc.save("transformed_document.mdp")
```

## Advanced Batch Processing

For processing multiple documents efficiently:

```python
from datapack import DocumentBatch, Document
import os

# Create a batch from a directory
batch = DocumentBatch.from_directory("./documents/", recursive=True)

# Filter documents by criteria
markdown_docs = batch.filter(lambda doc: doc.source_format == "markdown")
large_docs = batch.filter(lambda doc: len(doc.content) > 10000)
recent_docs = batch.filter(lambda doc: hasattr(doc.metadata, "updated_at") and 
                                      doc.metadata.updated_at > "2023-01-01")

# Process documents in parallel
batch.process_parallel(
    lambda doc: doc.add_metadata(processed=True),
    max_workers=4
)

# Apply complex transformation to all documents
def enhance_document(doc):
    # Add standard headers
    if not doc.content.startswith("# "):
        doc.content = f"# {doc.metadata.title}\n\n{doc.content}"
    
    # Add footer with metadata
    footer = f"\n\n---\nLast updated: {doc.metadata.updated_at if hasattr(doc.metadata, 'updated_at') else 'unknown'}"
    doc.content += footer
    
    # Add standard tags
    if not hasattr(doc.metadata, "tags"):
        doc.metadata.tags = []
    doc.metadata.tags.extend(["processed", "enhanced"])
    
    return doc

enhanced_batch = batch.map(enhance_document)

# Save all processed documents
enhanced_batch.save_all(output_dir="./enhanced/", format="mdp")
```

## Document Collections and Search

Working with collections of documents and implementing search:

```python
from datapack import DocumentCollection, Document, SearchIndex
import os

# Create a collection
collection = DocumentCollection("Documentation Collection")

# Add documents from a directory
doc_dir = "./documents/"
for filename in os.listdir(doc_dir):
    if filename.endswith(".mdp"):
        doc = Document.from_file(os.path.join(doc_dir, filename))
        collection.add(doc)

# Create a search index
index = SearchIndex()
index.index_collection(collection)

# Search documents
results = index.search("machine learning algorithms")
print(f"Found {len(results)} matching documents")

for score, doc in results:
    print(f"Score: {score:.2f} - {doc.metadata.title}")
    
# More specific search
advanced_results = index.search(
    query="security encryption",
    filters={
        "tags": ["advanced", "security"],
        "document_type": "tutorial"
    }
)

# Save the collection with its index
collection.save("documentation_collection.json")
index.save("documentation_index.json")
```

## Template System

Datapack provides a template system for creating consistent documents:

```python
from datapack import Document, Template
from datetime import datetime

# Create a document template
template = Template(
    content="""# {title}

Created by: {author}
Date: {date}

## Overview

{overview}

## Details

{details}

## Conclusion

{conclusion}
""",
    metadata_template={
        "title": "",
        "author": "Datapack User",
        "created_at": lambda: datetime.now().isoformat(),
        "version": "1.0.0",
        "status": "draft",
        "tags": ["documentation"]
    }
)

# Create a document from the template
doc = template.create(
    content_vars={
        "title": "Template Example",
        "author": "John Doe",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "overview": "This is an overview of the document.",
        "details": "These are the details of the document.",
        "conclusion": "This is the conclusion of the document."
    },
    metadata={
        "title": "Template Example",
        "author": "John Doe",
        "tags": ["template", "example"]
    }
)

# Save the document
doc.save("template_example.mdp")
```

## Next Steps

Now that you've explored Datapack's advanced features, you might want to:

- Learn about [Security & Sharing](security-sharing.md) for collaboration workflows
- Check out the [API Reference](../api/core.md) for detailed API documentation
- See [Example Applications](../examples/index.md) for real-world use cases
- Explore [Integration](../integration/index.md) with other tools and platforms 