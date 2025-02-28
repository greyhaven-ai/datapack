# Datapack

Datapack is a powerful platform for document ingestion, parsing, annotation, and secure sharing across software ecosystems. It provides a comprehensive set of tools for working with various document types and integrating with Large Language Models (LLMs).

Datapack uses the standalone [Markdown Data Package (MDP)](https://github.com/yourusername/mdp) format as its native document format, providing a standardized way to work with documents.

## Key Features

- **Document Processing**: Ingest and parse documents in multiple formats (PDF, Word, CSV, JSON, XML, Markdown, HTML)
- **Format Converters**: Transform JSON, XML, CSV, YAML, Markdown, PDF, HTML, DOCX, Jupyter Notebooks, Email, SQL, and API responses into MDP documents
- **Metadata & Annotations**: Add rich metadata and annotations to documents
- **Context-Aware**: Build and maintain relationships between documents and their contexts
- **Secure Sharing**: Share documents securely across different software systems
- **LLM Integration**: Seamlessly integrate with powerful language models
- **AI-Powered Collections**: Automatically organize documents into thematic collections with intelligent parent documents
- **User-Friendly API**: Work with documents easily using our intuitive high-level API

## Installation

```bash
# Basic installation
pip install datapack

# With basic converters (JSON, XML, CSV, YAML, Markdown)
pip install datapack[converters]

# With document converters (DOCX, Jupyter Notebooks)
pip install datapack[documents]

# With PDF support
pip install datapack[pdf]

# Full installation with all features
pip install datapack[full]

# For development
pip install datapack[dev]
```

## Quick Start

### Working with MDP Documents

Datapack uses the [Markdown Data Package (MDP)](https://github.com/yourusername/mdp) format, which combines the readability of Markdown with structured metadata capabilities.

```python
from mdp import Document

# Create a new document
doc = Document.create(
    title="My First Document",
    content="# Hello World\n\nThis is my first MDP document.",
    author="John Doe",
    tags=["example", "tutorial"]
)

# Save to an MDP file
doc.save("my_document.mdp")

# Load from an MDP file
loaded_doc = Document.from_file("my_document.mdp")

# Access properties
print(loaded_doc.title)  # "My First Document"
print(loaded_doc.author)  # "John Doe"
print(loaded_doc.tags)    # ["example", "tutorial"]

# Update properties
loaded_doc.title = "Updated Title"
loaded_doc.add_tag("updated")

# Save changes
loaded_doc.save()
```

### Working with Document Collections

```python
from mdp import Collection, Document

# Create a collection
collection = Collection("My Collection")

# Add documents
doc1 = Document.create(title="First Document", content="# First Document")
doc2 = Document.create(title="Second Document", content="# Second Document")

collection.add_document(doc1)
collection.add_document(doc2)

# Create relationships between documents
doc1.add_relationship(doc2, relationship_type="related")

# Save all documents in a collection
collection.save_all("documents/")

# Load a collection from a directory
loaded_collection = Collection.from_directory("documents/")
```

### AI-Powered Document Collections

Datapack now provides AI capabilities to automatically organize documents into thematic collections:

```python
import asyncio
from pathlib import Path
from datapack.ai.agents import CollectionCreationAgent

# Create a collection creation agent
agent = CollectionCreationAgent()

# List of documents to process
documents = [
    "research_ml.md",
    "research_nlp.md",
    "budget_2023.md",
    "budget_2024.md",
    "product_roadmap.md",
    "team_structure.md"
]

# Create a collection with a parent document
async def create_research_collection():
    collection = await agent.create_collection_from_documents(
        documents=["research_ml.md", "research_nlp.md"],
        collection_name="Research Materials",
        base_path=Path("./collections"),
        organization_strategy="thematic",
        create_parent_document=True
    )
    return collection

# Organize all documents by theme automatically
async def organize_by_theme():
    collections = await agent.organize_documents_by_theme(
        documents=documents,
        base_path=Path("./collections"),
        max_collections=3
    )
    return collections

# Example usage
research_collection = asyncio.run(create_research_collection())
themed_collections = asyncio.run(organize_by_theme())

# Access the auto-created collections
for collection in themed_collections:
    print(f"Collection: {collection.name}")
    print(f"Parent document: {collection.documents[0].title}")
    print(f"Member documents: {len(collection.documents) - 1}")
```

### Converting Documents to MDP Format

Datapack provides converters for transforming various data formats into MDP documents:

```python
from datapack.converters import (
    # Basic converters
    json_to_mdp,
    xml_to_mdp,
    csv_to_mdp,
    yaml_to_mdp,
    markdown_to_mdp,
    
    # Advanced converters
    api_response_to_mdp,
    sql_to_mdp,
    query_results_to_mdp
)

# Try to import converters that require additional dependencies
try:
    from datapack.converters import html_to_mdp
except ImportError:
    pass  # HTML support not available

try:
    from datapack.converters import docx_to_mdp
except ImportError:
    pass  # DOCX support not available

try:
    from datapack.converters import notebook_to_mdp
except ImportError:
    pass  # Jupyter Notebook support not available

try:
    from datapack.converters import email_to_mdp
except ImportError:
    pass  # Email support not available

try:
    from datapack.converters import pdf_to_mdp
except ImportError:
    pass  # PDF support not available

# Convert JSON to MDP
json_doc = json_to_mdp(
    json_data={"title": "JSON Example", "data": {"key": "value"}},
    output_path="json_example.mdp",
    extract_metadata=True
)

# Convert XML to MDP
xml_doc = xml_to_mdp(
    xml_data="<root><title>XML Example</title><content>Some content</content></root>",
    output_path="xml_example.mdp",
    metadata_xpath={"title": "//title"}
)

# Convert CSV to MDP
csv_doc = csv_to_mdp(
    csv_data="id,name\n1,Item 1\n2,Item 2",
    output_path="csv_example.mdp",
    metadata={"title": "CSV Example"},
    include_stats=True
)

# Convert YAML to MDP
yaml_doc = yaml_to_mdp(
    yaml_data="title: YAML Example\ncontent: Some content",
    output_path="yaml_example.mdp",
    extract_metadata=True
)

# Convert Markdown to MDP
markdown_doc = markdown_to_mdp(
    markdown_data="# Markdown Example\n\nSome content",
    output_path="markdown_example.mdp",
    extract_metadata=True
)

# Convert HTML to MDP
if 'html_to_mdp' in locals():
    html_doc = html_to_mdp(
        html_data="<html><head><title>HTML Example</title></head><body><h1>Hello World</h1></body></html>",
        output_path="html_example.mdp",
        extract_metadata=True
    )

# Convert DOCX to MDP
if 'docx_to_mdp' in locals():
    docx_doc = docx_to_mdp(
        docx_data="document.docx",
        output_path="docx_example.mdp",
        extract_metadata=True
    )

# Convert Jupyter Notebook to MDP
if 'notebook_to_mdp' in locals():
    notebook_doc = notebook_to_mdp(
        notebook_data="notebook.ipynb",
        output_path="notebook_example.mdp",
        extract_metadata=True,
        include_outputs=True
    )

# Convert Email to MDP
if 'email_to_mdp' in locals():
    email_doc = email_to_mdp(
        email_data="email.eml",
        output_path="email_example.mdp",
        extract_metadata=True
    )

# Convert SQL to MDP
sql_doc = sql_to_mdp(
    sql_data="SELECT * FROM users WHERE active = true;",
    output_path="sql_example.mdp",
    format_sql=True
)

# Convert SQL query results to MDP
results = [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "Jane", "email": "jane@example.com"}
]
query_results_doc = query_results_to_mdp(
    results=results,
    query="SELECT id, name, email FROM users WHERE active = true;",
    output_path="query_results_example.mdp"
)

# Convert API response to MDP
api_doc = api_response_to_mdp(
    response_data={"status": "success", "data": {"users": [{"id": 1, "name": "John"}]}},
    output_path="api_example.mdp",
    format_type="json",
    url="https://api.example.com/users",
    method="GET",
    status_code=200
)

# Convert PDF to MDP (requires PDF support)
if 'pdf_to_mdp' in locals():
    pdf_doc = pdf_to_mdp(
        pdf_data="document.pdf",
        output_path="pdf_example.mdp",
        extract_metadata=True,
        max_pages=10  # Limit to first 10 pages
    )
```

### New Feature: Automatic Metadata Extraction

Datapack includes functionality to automatically extract metadata from document content:

```python
from datapack.ai import enhance_document
from mdp import Document

# Create a basic document
doc = Document.create(
    content="""# Machine Learning Basics
    
    This document covers the fundamentals of machine learning,
    including supervised learning, neural networks, and model evaluation.
    """
)

# Use Datapack's AI to enhance the document with metadata
enhanced_doc = enhance_document(doc)

# The metadata will be automatically extracted:
print(enhanced_doc.title)  # "Machine Learning Basics"
print(enhanced_doc.tags)   # ["machine", "learning", "neural", "networks", "model"]
```

### Command-Line Interface

Datapack includes a CLI for common tasks:

```bash
# Convert files to MDP format
datapack convert --input data.json --output document.mdp --format json
datapack convert --input data.xml --output document.mdp --format xml
datapack convert --input data.csv --output document.mdp --format csv
datapack convert --input data.yaml --output document.mdp --format yaml
datapack convert --input document.md --output document.mdp --format markdown
datapack convert --input document.html --output document.mdp --format html
datapack convert --input document.docx --output document.mdp --format docx
datapack convert --input notebook.ipynb --output document.mdp --format notebook
datapack convert --input email.eml --output document.mdp --format email
datapack convert --input query.sql --output document.mdp --format sql
datapack convert --input document.pdf --output document.mdp --format pdf

# Convert with additional options
datapack convert -i data.csv -o output.mdp --extract-metadata --include-stats
datapack convert -i document.pdf -o output.mdp --max-pages 5
datapack convert -i document.md -o output.mdp --preserve-frontmatter
datapack convert -i notebook.ipynb -o output.mdp --include-outputs

# Add custom metadata during conversion
datapack convert -i data.json -o output.mdp -m "title=Custom Title,author=John Doe,tags=[tag1,tag2,tag3]"

# Create AI-powered document collections
datapack ai create-collection -i doc1.md doc2.md doc3.md -o collections/ -n "Research Materials"
datapack ai organize-by-theme -i *.md -o collections/ --max-collections 3 --min-docs 2

# Get help for commands
datapack convert --help
datapack ai --help
```

## Developer Workflows

Datapack provides tools for integrating with development workflows:

```python
from datapack.workflows import (
    sync_codebase_docs,
    generate_api_docs,
    create_release_notes
)

# Generate documentation from code comments
docs = sync_codebase_docs(
    code_directory="./src",
    docs_directory="./docs",
    file_patterns=["*.py", "*.js"]
)

# Create API reference
api_doc = generate_api_docs(
    code_directory="./src",
    output_file="./docs/api_reference.mdp",
    module_name="MyModule"
)

# Generate release notes
release_doc = create_release_notes(
    version="1.0.0",
    output_file="./docs/release_notes.mdp",
    changes=[
        {"type": "feat", "description": "Added new feature X"},
        {"type": "fix", "description": "Fixed critical bug Y"}
    ],
    project_name="MyProject"
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

License Disclaimer

This project is primarily licensed under the GNU Affero General Public License v3.0 (AGPL-3.0), as specified in the LICENSE file in the root directory of this repository.

Please note:

The AGPL-3.0 license applies to all parts of the project unless otherwise specified.
The SDKs and clients may be licensed under the MIT License. Refer to the LICENSE files in these specific directories for details.
When using or contributing to this project, ensure you comply with the appropriate license terms for the specific component you are working with.
For more details on the licensing of specific components, please refer to the LICENSE files in the respective directories or contact the project maintainers.
