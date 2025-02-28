# Datapack AI Module

This module provides AI-powered document processing capabilities for the Datapack platform.

## Overview

The AI module enables:

- Metadata extraction from documents
- Document structure analysis
- Content enhancement and summarization
- Relationship identification between documents
- Document collection organization and management

The module integrates with PydanticAI to provide type-safe AI interactions with well-defined input and output structures.

## Key Components

### Models

- `AIModelConfig`: Configuration for AI models (provider, model name, temperature)
- `DocumentMetadata`: Pydantic model representing document metadata
- `DocumentStructure`: Structured representation of document content
- `Relationship`: Representation of relationships between documents

### Extractors

- `MetadataExtractor`: Extracts metadata from document content
- `ContentStructureExtractor`: Analyzes document structure
- `RelationshipExtractor`: Identifies relationships between documents
- `PDFExtractor`: Specialized extractor for PDF documents with image support

### Agents

- `DocumentProcessingAgent`: High-level agent for document processing
- `ContentEnhancementAgent`: Improves and enhances document content
- `CollectionCreationAgent`: Organizes documents into collections

## Collection Creation

The `CollectionCreationAgent` provides powerful capabilities for organizing multiple documents into collections with:

- Thematic grouping based on content
- Creation of parent/cover documents that include summaries and references
- Automatic relationship extraction between documents
- Custom organization strategies (thematic, chronological, hierarchical)

### How It Works

The collection creation process:

1. Documents are analyzed to extract metadata and content structure
2. Relationships between documents are identified
3. Documents are organized into logical collections based on content themes
4. A parent document is created as a "cover page" that includes:
   - Collection metadata
   - Document summaries
   - Reference links to all collection members
   - Visualized relationships between documents

This approach uses a standard .mdp file as the parent document, maintaining compatibility with the MDP format while enabling rich connections between documents.

## Usage Examples

### Basic Document Processing

```python
from pathlib import Path
from datapack.ai.agents import DocumentProcessingAgent

# Create an agent
agent = DocumentProcessingAgent()

# Process a document
result = agent.process(
    document="path/to/document.txt",
    extract_metadata=True,
    extract_structure=True
)

# Access enhanced document
document = result["document"]
document.save("enhanced.mdp")
```

### Creating a Collection

```python
import asyncio
from pathlib import Path
from datapack.ai.agents import CollectionCreationAgent

# Create a collection creation agent
agent = CollectionCreationAgent()

# List of documents to process
documents = [
    "path/to/doc1.md",
    "path/to/doc2.txt",
    "path/to/doc3.pdf"
]

# Create a collection
async def create_collection():
    collection = await agent.create_collection_from_documents(
        documents=documents,
        collection_name="Research Materials",
        base_path=Path("./collections"),
        organization_strategy="thematic",
        create_parent_document=True
    )
    return collection

# Run the async function
collection = asyncio.run(create_collection())

# Access the parent document (cover page)
parent_doc = collection.documents[0]
print(f"Cover page: {parent_doc.title}")
```

### Organizing Documents by Theme

```python
import asyncio
from pathlib import Path
from datapack.ai.agents import CollectionCreationAgent

# Create a collection creation agent
agent = CollectionCreationAgent()

# List of documents to process
documents = [
    "path/to/doc1.md",
    "path/to/doc2.txt",
    "path/to/doc3.pdf",
    "path/to/doc4.md",
    "path/to/doc5.md",
]

# Organize documents into thematic collections
async def organize_documents():
    collections = await agent.organize_documents_by_theme(
        documents=documents,
        base_path=Path("./collections"),
        max_collections=3,
        min_documents_per_collection=2
    )
    return collections

# Run the async function
collections = asyncio.run(organize_documents())

# Print collection information
for collection in collections:
    print(f"Collection: {collection.name}")
    print(f"Documents: {len(collection.documents)}")
    print("Document titles:")
    for doc in collection.documents[1:]:  # Skip parent document
        print(f"- {doc.title}")
    print()
```

## Command Line Usage

The AI functionality is also available through the command line:

```bash
# Extract metadata from a document
datapack ai extract-metadata -i document.txt -o metadata.json

# Enhance a document with AI processing
datapack ai enhance -i document.txt -o enhanced.mdp

# Create a collection from multiple documents
datapack ai create-collection -i doc1.md doc2.txt doc3.pdf -o collections/ -n "Research Materials"

# Organize documents into thematic collections
datapack ai organize-by-theme -i doc1.md doc2.txt doc3.pdf doc4.md -o collections/
```

## Development

To extend the AI functionality:

1. Define new model classes in `models.py` using Pydantic
2. Implement extractors in `extractors.py` for specific extraction tasks
3. Create agents in `agents.py` for coordinating higher-level processes
4. Update the CLI in `datapack/cli/ai.py` to expose new functionality

## Dependencies

- `pydantic-ai`: Type-safe AI interactions
- `mdp`: Markdown Data Pack file format support
- AI provider libraries (OpenAI, Google Gemini, Anthropic Claude) 