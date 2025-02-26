# Custom Metadata Examples

This guide demonstrates how to create and work with custom metadata schemas in Datapack, allowing you to define specialized metadata for your specific use cases.

## Introduction to Custom Metadata

While Datapack provides standard metadata fields (title, author, etc.), many applications require domain-specific metadata. Custom metadata schemas allow you to define structured metadata specific to your use case, whether it's research papers, legal documents, product documentation, or any other specialized content.

## Defining Custom Metadata Schemas

Let's create several examples of custom metadata schemas for different document types:

### Research Paper Metadata Schema

```python
from datapack import Document, MetadataSchema, Field
from datetime import date
from typing import List, Optional

# Define a research paper metadata schema
class ResearchPaperMetadata(MetadataSchema):
    title: str
    authors: List[str]
    abstract: str
    publication_date: date
    journal: Optional[str] = None
    volume: Optional[int] = None
    issue: Optional[int] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    keywords: List[str] = []
    funding_sources: List[str] = []
    citations: int = 0
    peer_reviewed: bool = True

# Create a document with the custom metadata schema
research_paper = Document(
    content="# Sample Research Paper\n\nThis is the content of a research paper.",
    metadata=ResearchPaperMetadata(
        title="Advances in Document Processing with Datapack",
        authors=["Jane Smith", "John Doe"],
        abstract="This paper discusses the advanced document processing capabilities of Datapack.",
        publication_date=date(2023, 6, 15),
        journal="Journal of Document Engineering",
        volume=12,
        issue=3,
        pages="45-58",
        doi="10.1234/jde.2023.123",
        keywords=["document processing", "metadata", "Datapack"],
        funding_sources=["National Science Foundation", "Tech Innovation Grant"],
        citations=42
    )
)

# Save the document with custom metadata
research_paper.save("research_paper.mdp")

print("Research paper metadata example created")
```

### Technical Documentation Metadata Schema

```python
from datapack import Document, MetadataSchema, Field
from datetime import date
from typing import List, Dict, Optional, Union

# Define a technical documentation metadata schema
class TechnicalDocMetadata(MetadataSchema):
    title: str
    product: str
    version: str
    author: str
    contributors: List[str] = []
    created_date: date
    last_updated: date
    status: str = "draft"  # draft, review, approved, published
    audience: List[str] = ["developers"]  # developers, admins, end-users
    platforms: List[str] = []
    related_docs: List[str] = []
    prerequisites: List[str] = []
    tags: List[str] = []
    category: Optional[str] = None
    examples_tested: bool = False
    review_history: List[Dict[str, Union[str, date]]] = []

# Create a document with the custom metadata schema
tech_doc = Document(
    content="# API Documentation\n\nThis document describes the API for the product.",
    metadata=TechnicalDocMetadata(
        title="REST API Reference",
        product="DataService Pro",
        version="2.1.0",
        author="Documentation Team",
        contributors=["Alice Johnson", "Bob Williams"],
        created_date=date(2023, 5, 10),
        last_updated=date(2023, 6, 20),
        status="published",
        audience=["developers", "administrators"],
        platforms=["Linux", "Windows", "macOS"],
        related_docs=["getting_started.mdp", "authentication.mdp", "examples.mdp"],
        prerequisites=["Basic REST knowledge", "JSON understanding"],
        tags=["api", "rest", "reference", "http"],
        category="Developer Reference",
        examples_tested=True,
        review_history=[
            {"reviewer": "Senior Developer", "date": date(2023, 6, 1), "status": "approved"},
            {"reviewer": "Technical Editor", "date": date(2023, 6, 15), "status": "approved"}
        ]
    )
)

# Save the document
tech_doc.save("technical_doc.mdp")

print("Technical documentation metadata example created")
```

### Legal Document Metadata Schema

```python
from datapack import Document, MetadataSchema, Field
from datetime import date
from typing import List, Dict, Optional

# Define a legal document metadata schema
class LegalDocumentMetadata(MetadataSchema):
    title: str
    document_type: str  # contract, agreement, policy, etc.
    parties: List[str]
    effective_date: date
    expiration_date: Optional[date] = None
    jurisdiction: str
    governing_law: str
    confidentiality: str = "confidential"  # public, confidential, restricted
    status: str = "draft"  # draft, review, final, executed
    version: str
    authors: List[str]
    signatories: List[Dict[str, str]] = []
    related_documents: List[str] = []
    amendments: List[Dict[str, Union[str, date]]] = []
    tags: List[str] = []
    reviewed_by_legal: bool = False

# Create a document with the custom metadata schema
legal_doc = Document(
    content="# Service Agreement\n\nThis Service Agreement (\"Agreement\") is entered into by the parties listed below.",
    metadata=LegalDocumentMetadata(
        title="Master Service Agreement",
        document_type="agreement",
        parties=["Acme Corporation", "XYZ Services Inc."],
        effective_date=date(2023, 7, 1),
        expiration_date=date(2025, 6, 30),
        jurisdiction="California, USA",
        governing_law="California Law",
        confidentiality="confidential",
        status="final",
        version="1.0",
        authors=["Legal Department"],
        signatories=[
            {"name": "John Smith", "title": "CEO, Acme Corporation", "date": "2023-06-25"},
            {"name": "Sarah Jones", "title": "President, XYZ Services Inc.", "date": "2023-06-26"}
        ],
        related_documents=["statement_of_work.mdp", "terms_and_conditions.mdp"],
        tags=["agreement", "services", "legal"],
        reviewed_by_legal=True
    )
)

# Save the document
legal_doc.save("legal_doc.mdp")

print("Legal document metadata example created")
```

## Working with Custom Metadata

Once you've defined your custom metadata schema, you can work with it just like standard metadata:

### Accessing Custom Metadata

```python
from datapack import Document

# Load a document with custom metadata
doc = Document.from_file("research_paper.mdp")

# Access custom metadata fields
print(f"Title: {doc.metadata.title}")
print(f"Authors: {', '.join(doc.metadata.authors)}")
print(f"Publication Date: {doc.metadata.publication_date}")
print(f"Keywords: {', '.join(doc.metadata.keywords)}")
print(f"Citations: {doc.metadata.citations}")

# Check if metadata has specific fields
if hasattr(doc.metadata, "doi"):
    print(f"DOI: {doc.metadata.doi}")
```

### Updating Custom Metadata

```python
from datapack import Document
from datetime import date

# Load a document with custom metadata
doc = Document.from_file("technical_doc.mdp")

# Update metadata fields
doc.metadata.status = "published"
doc.metadata.last_updated = date.today()
doc.metadata.version = "2.1.1"
doc.metadata.examples_tested = True

# Add to list fields
doc.metadata.tags.append("updated")
doc.metadata.contributors.append("Charlie Brown")

# Add new review history entry
doc.metadata.review_history.append({
    "reviewer": "Product Manager",
    "date": date.today(),
    "status": "approved"
})

# Save the updated document
doc.save("technical_doc_updated.mdp")

print("Updated document saved")
```

## Validating Custom Metadata

Datapack can validate metadata against your schema:

```python
from datapack import Document, MetadataValidator, MetadataSchema
from typing import List, Optional

# Define a simple metadata schema
class ProductDocumentation(MetadataSchema):
    title: str
    product_name: str
    version: str
    features: List[str] = []
    deprecated: bool = False
    min_requirements: Optional[dict] = None

# Create a validator
validator = MetadataValidator(ProductDocumentation)

# Create a document with valid metadata
valid_doc = Document(
    content="# Product Documentation",
    metadata={
        "title": "Product X User Guide",
        "product_name": "Product X",
        "version": "1.0.0",
        "features": ["Feature A", "Feature B"],
        "deprecated": False,
        "min_requirements": {
            "os": "Windows 10",
            "ram": "4GB"
        }
    }
)

# Validate the metadata
is_valid, errors = validator.validate(valid_doc.metadata)
print(f"Valid metadata: {is_valid}")

# Create a document with invalid metadata
invalid_doc = Document(
    content="# Product Documentation",
    metadata={
        "title": "Product Y User Guide",
        "product_name": "Product Y",
        # Missing required 'version' field
        "features": ["Feature A", "Feature B"],
        "deprecated": "No"  # Should be boolean
    }
)

# Validate the metadata
is_valid, errors = validator.validate(invalid_doc.metadata)
print(f"Valid metadata: {is_valid}")
if not is_valid:
    print("Validation errors:")
    for field, error in errors.items():
        print(f"  - {field}: {error}")
```

## Searching and Filtering with Custom Metadata

Custom metadata can be used for searching and filtering documents:

```python
from datapack import DocumentCollection, Document
import os

# Create a collection
collection = DocumentCollection("Research Papers")

# Add documents to the collection
for filename in os.listdir():
    if filename.endswith(".mdp"):
        doc = Document.from_file(filename)
        collection.add(doc)

# Filter documents by custom metadata
peer_reviewed = collection.filter(lambda doc: doc.metadata.peer_reviewed if hasattr(doc.metadata, "peer_reviewed") else False)
recent_papers = collection.filter(lambda doc: hasattr(doc.metadata, "publication_date") and doc.metadata.publication_date.year >= 2022)
high_citations = collection.filter(lambda doc: hasattr(doc.metadata, "citations") and doc.metadata.citations > 10)

# Search for documents with specific keywords
ml_papers = collection.filter(lambda doc: hasattr(doc.metadata, "keywords") and "machine learning" in doc.metadata.keywords)

# Combine filters
important_ml_papers = collection.filter(
    lambda doc: (hasattr(doc.metadata, "keywords") and "machine learning" in doc.metadata.keywords) and
               (hasattr(doc.metadata, "citations") and doc.metadata.citations > 50)
)

print(f"Found {len(peer_reviewed)} peer-reviewed papers")
print(f"Found {len(recent_papers)} papers published since 2022")
print(f"Found {len(high_citations)} papers with more than 10 citations")
print(f"Found {len(ml_papers)} papers about machine learning")
print(f"Found {len(important_ml_papers)} highly-cited papers about machine learning")
```

## Custom Metadata Templates

You can create reusable metadata templates for common document types:

```python
from datapack import Document, MetadataTemplate
from datetime import date

# Create a blog post metadata template
blog_post_template = MetadataTemplate(
    title="",
    author="Content Team",
    publication_date=date.today(),
    status="draft",
    category="Technology",
    tags=[],
    allow_comments=True,
    featured=False,
    excerpt=""
)

# Create a document using the template
blog1 = Document(
    content="# New Blog Post\n\nThis is a new blog post.",
    metadata=blog_post_template.create(
        title="Introduction to Datapack",
        tags=["datapack", "tutorial", "metadata"],
        excerpt="Learn about Datapack's powerful document processing capabilities."
    )
)

# Create another document using the same template
blog2 = Document(
    content="# Advanced Metadata\n\nThis blog post covers advanced metadata concepts.",
    metadata=blog_post_template.create(
        title="Advanced Metadata in Datapack",
        author="Jane Smith", # Override the template default
        tags=["datapack", "advanced", "metadata"],
        category="Advanced Tutorials", # Override the template default
        featured=True, # Override the template default
        excerpt="Dive deeper into metadata capabilities with Datapack."
    )
)

blog1.save("blog1.mdp")
blog2.save("blog2.mdp")

print("Blog posts created from template")
```

## Exporting Custom Metadata

You can export custom metadata to various formats:

```python
from datapack import Document

# Load a document with custom metadata
doc = Document.from_file("research_paper.mdp")

# Export metadata to dict
metadata_dict = doc.metadata.to_dict()
print("Metadata as dictionary:", metadata_dict)

# Export metadata to JSON
metadata_json = doc.metadata.to_json()
print("Metadata as JSON:", metadata_json)

# Export select fields to CSV-compatible format
csv_data = {
    "title": doc.metadata.title,
    "authors": "|".join(doc.metadata.authors),
    "publication_date": str(doc.metadata.publication_date),
    "citations": doc.metadata.citations
}
print("Metadata for CSV:", csv_data)
```

## Best Practices for Custom Metadata

When designing custom metadata schemas, follow these best practices:

1. **Define Clear Schemas**: Create well-defined schemas with appropriate types
2. **Use Type Annotations**: Leverage Python type hints for better validation
3. **Provide Defaults**: Set sensible defaults for optional fields
4. **Document Your Schema**: Document the purpose and usage of each field
5. **Validate Early**: Validate metadata when documents are created or modified
6. **Be Consistent**: Use consistent naming conventions and field structures
7. **Consider Extensibility**: Design schemas that can evolve over time
8. **Separate Concerns**: Create different schemas for different document types
9. **Reuse Components**: Define reusable components for common metadata patterns
10. **Follow Standards**: When applicable, align with industry metadata standards

## Next Steps

Now that you understand how to work with custom metadata, you can:

- Learn about [Document Relationships](../relationships/document-relationships.md) to connect related documents
- Explore [Adding Context](../context/adding-context.md) to add contextual information to documents
- See how to implement [Context Processing](../context/context-processing.md) with your custom metadata 