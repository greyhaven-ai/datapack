# Document Parsing Example

This example demonstrates how to parse different document formats using Datapack, extracting content and metadata from each format.

## Prerequisites

For this example, you'll need:

- Datapack installed with format-specific extras: `pip install datapack[pdf,docx,html]`
- Sample documents in different formats (provided in code or create your own)

## Parsing Different Document Formats

Datapack provides a unified API for parsing documents in various formats. Here's how to parse different document types:

### Create Sample Documents

First, let's create sample documents in different formats to work with:

```python
import os

# Create a sample Markdown document
markdown_content = """---
title: Sample Markdown Document
author: Datapack User
tags: [markdown, sample]
---

# Sample Markdown Document

This is a sample **Markdown** document with some *formatting*.

## Section 1

- List item 1
- List item 2

## Section 2

[Link to example](https://example.com)
"""

# Create a sample HTML document
html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML Document</title>
    <meta name="author" content="Datapack User">
    <meta name="keywords" content="html, sample">
</head>
<body>
    <h1>Sample HTML Document</h1>
    <p>This is a sample <strong>HTML</strong> document with some <em>formatting</em>.</p>
    
    <h2>Section 1</h2>
    <ul>
        <li>List item 1</li>
        <li>List item 2</li>
    </ul>
    
    <h2>Section 2</h2>
    <p><a href="https://example.com">Link to example</a></p>
</body>
</html>
"""

# Create a sample plain text document
text_content = """Sample Text Document

This is a sample plain text document.

Section 1
---------
* List item 1
* List item 2

Section 2
---------
Link: https://example.com
"""

# Write the sample files
os.makedirs("sample_docs", exist_ok=True)

with open("sample_docs/sample.md", "w") as f:
    f.write(markdown_content)

with open("sample_docs/sample.html", "w") as f:
    f.write(html_content)

with open("sample_docs/sample.txt", "w") as f:
    f.write(text_content)

print("Sample documents created in 'sample_docs' directory")
```

### Parsing Markdown Documents

```python
from datapack import Document

# Parse a Markdown document
markdown_doc = Document.from_file("sample_docs/sample.md")

print("Markdown Document:")
print(f"Title: {markdown_doc.metadata.title}")
print(f"Author: {markdown_doc.metadata.author}")
print(f"Tags: {', '.join(markdown_doc.metadata.tags)}")
print(f"Content length: {len(markdown_doc.content)} characters")
print(f"First 100 chars: {markdown_doc.content[:100]}...")
print()

# Extract headings
headings = markdown_doc.get_headings()
print("Headings:")
for heading in headings:
    print(f"- Level {heading.level}: {heading.text}")
```

### Parsing HTML Documents

```python
from datapack import Document

# Parse an HTML document
html_doc = Document.from_file("sample_docs/sample.html")

print("HTML Document:")
print(f"Title: {html_doc.metadata.title}")
print(f"Author: {html_doc.metadata.author}")
print(f"Keywords: {html_doc.metadata.keywords}")
print(f"Content length: {len(html_doc.content)} characters")
print(f"First 100 chars: {html_doc.content[:100]}...")
print()

# Extract headings
headings = html_doc.get_headings()
print("Headings:")
for heading in headings:
    print(f"- Level {heading.level}: {heading.text}")
```

### Parsing Plain Text Documents

```python
from datapack import Document

# Parse a plain text document
text_doc = Document.from_file("sample_docs/sample.txt")

print("Plain Text Document:")
print(f"Content length: {len(text_doc.content)} characters")
print(f"First 100 chars: {text_doc.content[:100]}...")
print()

# Plain text documents don't have structured metadata by default
# We can add metadata programmatically
text_doc.metadata.title = "Sample Text Document"
text_doc.metadata.format = "plain text"
text_doc.metadata.extracted = True

# Now save as MDP to preserve the metadata
text_doc.save("sample_docs/sample_text.mdp")
```

### Parsing PDF Documents

PDF parsing requires the pdf extras to be installed: `pip install datapack[pdf]`.

For this example, let's assume you have a sample PDF file. If not, you can create one using a library like `reportlab` or use an existing PDF.

```python
from datapack import Document

# Parse a PDF document (assuming sample.pdf exists)
try:
    pdf_doc = Document.from_file("sample_docs/sample.pdf")
    
    print("PDF Document:")
    print(f"Title: {pdf_doc.metadata.title if hasattr(pdf_doc.metadata, 'title') else 'No title'}")
    print(f"Author: {pdf_doc.metadata.author if hasattr(pdf_doc.metadata, 'author') else 'No author'}")
    print(f"Content length: {len(pdf_doc.content)} characters")
    print(f"First 100 chars: {pdf_doc.content[:100]}...")
    print()
except FileNotFoundError:
    print("PDF example skipped: sample.pdf not found")
```

### Parsing Word Documents

Word document parsing requires the docx extras to be installed: `pip install datapack[docx]`.

For this example, let's assume you have a sample DOCX file. If not, you can create one using a library like `python-docx` or use an existing document.

```python
from datapack import Document

# Parse a Word document (assuming sample.docx exists)
try:
    docx_doc = Document.from_file("sample_docs/sample.docx")
    
    print("Word Document:")
    print(f"Title: {docx_doc.metadata.title if hasattr(docx_doc.metadata, 'title') else 'No title'}")
    print(f"Author: {docx_doc.metadata.author if hasattr(docx_doc.metadata, 'author') else 'No author'}")
    print(f"Content length: {len(docx_doc.content)} characters")
    print(f"First 100 chars: {docx_doc.content[:100]}...")
    print()
except FileNotFoundError:
    print("Word example skipped: sample.docx not found")
```

## Format-Specific Configuration

Datapack allows you to configure format-specific parsing options:

### Configuring Markdown Parsing

```python
from datapack import Document, MarkdownConfig

# Configure Markdown parsing
md_config = MarkdownConfig(
    extensions=["tables", "footnotes"],
    frontmatter=True,
    heading_style="atx"  # Use # style headings
)

# Parse with configuration
markdown_doc = Document.from_file(
    "sample_docs/sample.md", 
    config=md_config
)
```

### Configuring PDF Parsing

```python
from datapack import Document, PDFConfig

# Configure PDF parsing
pdf_config = PDFConfig(
    extract_images=True,
    detect_tables=True,
    ocr_enabled=False,  # Enable for scanned documents
    layout_analysis=True
)

# Parse with configuration (assuming sample.pdf exists)
try:
    pdf_doc = Document.from_file(
        "sample_docs/sample.pdf", 
        config=pdf_config
    )
except FileNotFoundError:
    print("PDF config example skipped: sample.pdf not found")
```

## Converting Between Formats

Once you've parsed documents, you can convert them to other formats:

```python
from datapack import Document

# Load a Markdown document
doc = Document.from_file("sample_docs/sample.md")

# Convert to different formats
doc.to_markdown("sample_docs/converted.md")
doc.to_html("sample_docs/converted.html")
doc.to_mdp("sample_docs/converted.mdp")  # Native format
doc.to_text("sample_docs/converted.txt")
doc.to_json("sample_docs/converted.json")

print("Document converted to various formats")
```

## Working with Unknown Formats

Datapack will attempt to detect the file format based on the file extension. For unknown formats, you can specify the format explicitly:

```python
from datapack import Document

# Parse a file with an unknown extension
try:
    doc = Document.from_file(
        "sample_docs/document.xyz",
        format="markdown"  # Force interpretation as markdown
    )
except FileNotFoundError:
    print("Unknown format example skipped: document.xyz not found")
```

## Batch Processing Multiple Formats

For processing multiple documents in different formats:

```python
from datapack import Document, DocumentBatch
import os

# Create a batch from directory
os.makedirs("sample_docs/processed", exist_ok=True)

# Process all documents in a directory
def process_directory(input_dir, output_dir):
    files_processed = 0
    for filename in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, filename)):
            try:
                # Load the document
                doc = Document.from_file(os.path.join(input_dir, filename))
                
                # Add some processing metadata
                doc.metadata.processed = True
                doc.metadata.processor = "Datapack"
                
                # Save as MDP
                doc.save(os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.mdp"))
                files_processed += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return files_processed

# Process all documents
num_processed = process_directory("sample_docs", "sample_docs/processed")
print(f"Processed {num_processed} documents")
```

## Complete Example

Here's a complete script that demonstrates parsing different document formats:

```python
from datapack import Document
import os

def setup_sample_docs():
    """Create sample documents for testing"""
    # Create directory
    os.makedirs("sample_docs", exist_ok=True)
    
    # Create Markdown
    with open("sample_docs/sample.md", "w") as f:
        f.write("""---
title: Sample Markdown Document
author: Datapack User
tags: [markdown, sample]
---

# Sample Markdown Document

This is a sample **Markdown** document.
""")
    
    # Create HTML
    with open("sample_docs/sample.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML Document</title>
    <meta name="author" content="Datapack User">
</head>
<body>
    <h1>Sample HTML Document</h1>
    <p>This is a sample HTML document.</p>
</body>
</html>
""")
    
    # Create Text
    with open("sample_docs/sample.txt", "w") as f:
        f.write("Sample Text Document\n\nThis is a sample text document.")
    
    return "sample_docs"

def parse_all_formats(directory):
    """Parse all document formats in the directory"""
    results = {}
    
    # Parse Markdown
    try:
        md_doc = Document.from_file(f"{directory}/sample.md")
        results["markdown"] = {
            "title": md_doc.metadata.title,
            "author": md_doc.metadata.author,
            "content_preview": md_doc.content[:50]
        }
    except Exception as e:
        results["markdown"] = f"Error: {e}"
    
    # Parse HTML
    try:
        html_doc = Document.from_file(f"{directory}/sample.html")
        results["html"] = {
            "title": html_doc.metadata.title,
            "author": html_doc.metadata.author,
            "content_preview": html_doc.content[:50]
        }
    except Exception as e:
        results["html"] = f"Error: {e}"
    
    # Parse Text
    try:
        text_doc = Document.from_file(f"{directory}/sample.txt")
        results["text"] = {
            "content_preview": text_doc.content[:50]
        }
    except Exception as e:
        results["text"] = f"Error: {e}"
        
    return results

def main():
    """Main function demonstrating document parsing"""
    print("Document Parsing Example")
    print("=======================\n")
    
    # Setup sample documents
    sample_dir = setup_sample_docs()
    print(f"Created sample documents in {sample_dir}\n")
    
    # Parse all formats
    results = parse_all_formats(sample_dir)
    
    # Display results
    print("Parsing Results:")
    print("---------------")
    
    for format_name, result in results.items():
        print(f"\n{format_name.upper()}:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {result}")
    
    print("\nExample completed!")

if __name__ == "__main__":
    main()
```

## Output

Running the complete example will produce output similar to:

```
Document Parsing Example
=======================

Created sample documents in sample_docs

Parsing Results:
---------------

MARKDOWN:
  title: Sample Markdown Document
  author: Datapack User
  content_preview: # Sample Markdown Document

This is a sample **Mark

HTML:
  title: Sample HTML Document
  author: Datapack User
  content_preview: Sample HTML Document

This is a sample HTML document.

TEXT:
  content_preview: Sample Text Document

This is a sample text document.

Example completed!
```

## Key Concepts

This example demonstrates several key concepts:

1. **Unified Parsing API**: Datapack provides a consistent API for parsing different document formats
2. **Metadata Extraction**: Different formats have different metadata capabilities that Datapack normalizes
3. **Format-Specific Configuration**: Each format can be configured with specific options
4. **Format Conversion**: Documents can be converted between formats
5. **Batch Processing**: Multiple documents can be processed efficiently

## Next Steps

Now that you understand how to parse different document formats, you can:

- Learn about [Metadata & Annotations](../../concepts/metadata-annotations.md) to add rich context to your documents
- Explore [Document Relationships](../relationships/document-relationships.md) to connect related documents
- See how to [Add Context](../context/adding-context.md) to make your documents more meaningful 