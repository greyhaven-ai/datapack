# Using Standard Metadata

This guide demonstrates how to work with standard metadata in Datapack using the MDP format.

## What is Standard Metadata?

Standard metadata refers to a predefined set of fields that provide consistent information about a document. Using standard metadata ensures that your documents have a predictable structure and can be processed uniformly across systems.

## Standard Metadata Fields

Datapack supports the following standard metadata fields:

| Field | Description | Type | Example |
|-------|-------------|------|---------|
| `title` | Document title | String | "Example Document" |
| `description` | Brief description | String | "This is an example" |
| `version` | Document version | String | "1.0.0" |
| `type` | Document type | String | "example" |
| `author` | Document author | String | "John Doe" |
| `contributors` | List of contributors | Array | ["Jane Smith", "Bob Johnson"] |
| `created_at` | Creation date | ISO Date | "2023-05-15" |
| `updated_at` | Last update date | ISO Date | "2023-05-16" |
| `tags` | Categorization tags | Array | ["example", "metadata"] |
| `category` | Primary category | String | "documentation" |
| `status` | Document status | String | "published" |
| `source_file` | Original file name | String | "original.md" |
| `source_type` | Original file type | String | "markdown" |
| `source_url` | Source URL | String | "https://example.com" |
| `related_documents` | Related docs | Array | ["doc1.mdp", "doc2.mdp"] |
| `parent_document` | Parent document | String | "main.mdp" |

## Example MDP File with Standard Metadata

```mdp
---
title: Example Document with Standard Metadata
description: This document demonstrates the use of standard metadata fields
version: 1.0.0
type: example
author: Datapack Team
contributors:
- Contributor 1
- Contributor 2
created_at: '2023-05-15'
updated_at: '2023-05-16'
tags:
- example
- metadata
- mdp
category: documentation
status: published
source_file: original_document.md
source_type: markdown
source_url: https://example.com/original
related_documents:
- doc1.mdp
- doc2.mdp
parent_document: main_doc.mdp
---

# Example Document with Standard Metadata

This document demonstrates the use of standard metadata fields in MDP files.
```

## Working with Standard Metadata in Datapack

### Reading Metadata

```python
from datapack import Document

# Load a document
doc = Document.from_file("example.mdp")

# Access metadata fields
title = doc.metadata.title
author = doc.metadata.author
tags = doc.metadata.tags
```

### Adding or Updating Metadata

```python
from datapack import Document

# Create a new document
doc = Document()

# Set metadata fields
doc.metadata.title = "My Document"
doc.metadata.author = "Jane Smith"
doc.metadata.tags = ["example", "tutorial"]
doc.metadata.created_at = "2023-06-01"

# Save the document
doc.save("my_document.mdp")
```

## Benefits of Standard Metadata

1. **Consistency**: All documents follow the same structure
2. **Interoperability**: Different tools can work with the files predictably
3. **Validation**: Files can be validated against a schema
4. **Documentation**: Clear guidance for users creating MDP files

## Next Steps

- Learn about [Custom Metadata](custom-metadata.md)
- Explore [Document Relationships](../relationships/document-relationships.md)
- See how to use metadata in [Document Processing](../../concepts/document-processing.md) 