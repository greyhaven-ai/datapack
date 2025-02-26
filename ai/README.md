# Datapack AI Module

This module provides AI-powered capabilities for the datapack library, enabling automatic extraction, enhancement, and processing of document metadata and content.

## Features

- **Structured Metadata Extraction**: Extract metadata like titles, tags, summaries, and key points from document content using state-of-the-art LLMs
- **Content Structure Analysis**: Parse and understand document structure, including sections, headings, and relationships
- **Relationship Detection**: Automatically identify relationships between documents based on content references
- **Content Enhancement**: Generate summaries, annotations, and improvement suggestions for documents
- **High-Level Processing Agents**: Coordinate multiple operations with easy-to-use agent interfaces

## Dependencies

To use the AI module, you'll need:

1. **PydanticAI**: The core library for structured AI outputs
2. **At least one LLM provider**: OpenAI, Anthropic, Cohere, NVIDIA, or a local model
3. **Associated dependencies**: See `requirements.txt` for details

Install dependencies with:

```bash
pip install -r datapack/ai/requirements.txt
```

## Usage Examples

### Basic Metadata Extraction

```python
from datapack.ai.extractors import MetadataExtractor

# Create an extractor
extractor = MetadataExtractor(model="gpt-4o")  # Set your preferred model

# Extract metadata from content
metadata = extractor.extract_metadata(
    content="# My Document\n\nThis is a sample document about AI and data processing.",
    extract_title=True,
    extract_tags=True,
    extract_summary=True
)

print(f"Title: {metadata.title}")
print(f"Tags: {metadata.tags}")
print(f"Summary: {metadata.description}")
```

### Processing Multiple Documents

```python
from datapack.workflows.content import ai_process_documents

# Process all documents in a directory
documents, collection = ai_process_documents(
    source_directory="input_docs",
    output_directory="output_mdp",
    model="gpt-4o",
    recursive=True,
    analyze_relationships=True,
    enhancements=["summary", "annotations"]
)

print(f"Processed {len(documents)} documents")
```

### Enhancing a Single Document

```python
from datapack.mdp.document import Document
from datapack.workflows.content import ai_enhance_document

# Load an existing document
doc = Document.from_file("document.mdp")

# Enhance it with AI capabilities
enhanced_doc = ai_enhance_document(
    document=doc,
    enhancements=["tags", "summary", "annotations", "improvements"],
    model="gpt-4o"
)

# Save the enhanced document
enhanced_doc.save("enhanced_document.mdp")
```

## Configuration

The AI module respects the following environment variables:

- `DATAPACK_AI_MODEL`: Default model to use (e.g., "gpt-4o")
- `DATAPACK_API_KEY`: API key for the LLM provider
- `DATAPACK_AI_TEMPERATURE`: Temperature setting for generation (default: 0.0 for extractors, 0.3 for content enhancement)

You can set these in a `.env` file in your project root or through your environment.

## Model Support

The AI module supports multiple LLM providers through PydanticAI. Currently supported:

- OpenAI models (GPT-3.5, GPT-4, etc.)
- Anthropic models (Claude 2, Claude 3, etc.)
- Cohere models
- NVIDIA models
- Local models (through various wrappers)

## Customization

The AI module is designed to be easily extended for custom needs:

- Create new Pydantic models in `models.py` for structured outputs
- Add specialized extractors in `extractors.py`
- Create new agents in `agents.py` for higher-level processing
- Define custom system prompts in `prompts.py` 