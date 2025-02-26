# Context & Relationships

In Datapack, context and relationships are powerful concepts that allow documents to exist as part of a connected ecosystem rather than as isolated entities. This guide explains how Datapack implements these concepts and how you can leverage them in your applications.

## Understanding Context

Context in Datapack refers to the broader information environment in which a document exists. This includes:

1. **Document Context**: Information about the document's origin, purpose, and lifecycle
2. **Content Context**: The meaning and relevance of the document's content
3. **Relational Context**: How the document relates to other documents and information
4. **User Context**: How users interact with and interpret the document
5. **System Context**: The technical environment in which the document is processed

Context enables documents to be understood more comprehensively and processed more intelligently.

## Types of Relationships

Relationships in Datapack explicitly connect documents (or parts of documents) to other entities. The main types of relationships include:

### Document-to-Document Relationships

Connect one document to another, such as:

- **References**: When one document cites or references another
- **Versions**: When documents represent different versions of the same content
- **Derivatives**: When a document is derived from another
- **Compilations**: When documents are part of a larger collection

### Document-to-Entity Relationships

Connect documents to other types of entities:

- **Authors**: Linking to the creators of the document
- **Subjects**: Connecting to the topics or entities discussed
- **Systems**: Relating to the systems that process the document
- **Events**: Associating with events related to the document

### Internal Relationships

Establish connections within a document:

- **Cross-references**: Linking between different parts of the same document
- **Term definitions**: Connecting terms to their definitions
- **Structure relationships**: Mapping the hierarchical structure of the document

## Implementing Relationships

Datapack provides several ways to implement relationships:

### 1. Metadata-Based Relationships

The simplest approach uses metadata to reference related documents:

```yaml
---
title: Primary Document
related_documents:
  - document1.mdp
  - document2.mdp
parent_document: main.mdp
---
```

### 2. Relationship Objects

For more complex relationships, Datapack provides a dedicated Relationship class:

```python
from datapack import Document, Relationship

# Create documents
doc1 = Document(content="# Primary Document", metadata={"title": "Primary"})
doc2 = Document(content="# Related Document", metadata={"title": "Related"})

# Save documents
doc1.save("primary.mdp")
doc2.save("related.mdp")

# Create a relationship
relationship = Relationship(
    source="primary.mdp",
    target="related.mdp",
    type="references",
    metadata={
        "strength": "strong",
        "description": "Critical reference for understanding the primary document",
        "bidirectional": False
    }
)

# Add the relationship to the document
doc1.add_relationship(relationship)
doc1.save()
```

### 3. Context Networks

For advanced use cases, Datapack supports building context networks that represent complex webs of relationships:

```python
from datapack import ContextNetwork, Document

# Create a context network
network = ContextNetwork("Project Alpha")

# Add documents to the network
doc1 = Document.from_file("document1.mdp")
doc2 = Document.from_file("document2.mdp")
doc3 = Document.from_file("document3.mdp")

network.add_document(doc1)
network.add_document(doc2)
network.add_document(doc3)

# Create relationships in the network
network.add_relationship(doc1, doc2, "references")
network.add_relationship(doc2, doc3, "extends")
network.add_relationship(doc3, doc1, "provides_context_for")

# Save the network
network.save("project_alpha_context.json")
```

## Querying and Traversing Relationships

Datapack provides tools for working with relationships:

```python
from datapack import Document

# Load a document
doc = Document.from_file("document.mdp")

# Get all relationships
relationships = doc.get_relationships()

# Get specific types of relationships
references = doc.get_relationships(type="references")

# Find related documents
related_docs = doc.get_related_documents()

# Traverse a relationship chain (follow references of references)
chain = doc.traverse_relationships(max_depth=3)
```

## Context-Aware Processing

One of the most powerful features of Datapack is the ability to process documents with awareness of their context and relationships:

```python
from datapack import Document, ContextProcessor

# Load a document with its relationships
doc = Document.from_file("document.mdp", load_relationships=True)

# Create a context processor
processor = ContextProcessor()

# Process the document with context awareness
result = processor.process(
    document=doc,
    operation="summarize",
    context_depth=2  # Include relationships up to 2 levels deep
)

print(result.summary)
```

## Benefits of Context and Relationships

1. **Enhanced Understanding**: Documents can be understood in their broader context
2. **Richer Processing**: AI and processing systems can leverage contextual information
3. **Knowledge Graphs**: Facilitate building knowledge graphs based on document relationships
4. **Cross-Document Analysis**: Enable analysis across sets of related documents
5. **Contextual Security**: Implement security models that consider document relationships

## Best Practices

1. **Relationship Types**: Define a clear taxonomy of relationship types
2. **Bidirectionality**: Consider whether relationships should be bidirectional
3. **Metadata Enrichment**: Enrich relationships with descriptive metadata
4. **Context Boundaries**: Define appropriate boundaries for contextual processing
5. **Scalability**: Consider the scalability implications of complex relationship networks

## Next Steps

- Explore [Document Relationships Examples](../examples/relationships/document-relationships.md)
- Learn about [Cross-referencing](../examples/relationships/cross-referencing.md)
- See how to [Add Context to Documents](../examples/context/adding-context.md)
- Discover [Context Processing](../examples/context/context-processing.md) techniques 