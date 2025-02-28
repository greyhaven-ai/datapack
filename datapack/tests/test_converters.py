"""
Tests for the YAML, Markdown, and PDF converters.
"""

import os
import tempfile
import unittest
from pathlib import Path
import io

import yaml
import frontmatter

from mdp import Document
from datapack.converters import yaml_to_mdp, markdown_to_mdp

# Conditionally import PDF converter
try:
    from datapack.converters import pdf_to_mdp
    from pypdf import PdfReader, PdfWriter
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class TestYAMLConverter(unittest.TestCase):
    """Test cases for the YAML converter."""

    def setUp(self):
        """Set up test fixtures."""
        self.yaml_data = """
title: Test YAML Document
author: Test Author
created_at: 2023-06-01T10:00:00
tags:
  - yaml
  - test
  - converter

data:
  items:
    - id: 1
      name: Item 1
      value: 10.5
    - id: 2
      name: Item 2
      value: 20.75
  total: 31.25
"""
        self.yaml_dict = yaml.safe_load(self.yaml_data)
        
        # Create a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.temp_file.write(self.yaml_data.encode('utf-8'))
        self.temp_file.close()
        
        # Create a temporary output directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "output.mdp"

    def tearDown(self):
        """Tear down test fixtures."""
        os.unlink(self.temp_file.name)
        self.temp_dir.cleanup()

    def test_yaml_string_to_mdp(self):
        """Test converting YAML string to MDP."""
        doc = yaml_to_mdp(self.yaml_data)
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "Test YAML Document")
        self.assertEqual(doc.author, "Test Author")
        self.assertEqual(doc.metadata.get("created_at"), "2023-06-01T10:00:00")
        self.assertEqual(doc.tags, ["yaml", "test", "converter"])
        
        # Check source information
        self.assertEqual(doc.metadata.get("source", {}).get("type"), "yaml")
        self.assertIn("converter", doc.metadata.get("source", {}))
        self.assertIn("converted_at", doc.metadata.get("source", {}))

    def test_yaml_dict_to_mdp(self):
        """Test converting YAML dict to MDP."""
        doc = yaml_to_mdp(self.yaml_dict)
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "Test YAML Document")
        self.assertEqual(doc.author, "Test Author")
        self.assertEqual(doc.tags, ["yaml", "test", "converter"])

    def test_yaml_file_to_mdp(self):
        """Test converting YAML file to MDP."""
        doc = yaml_to_mdp(self.temp_file.name)
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "Test YAML Document")
        self.assertEqual(doc.author, "Test Author")
        self.assertEqual(doc.tags, ["yaml", "test", "converter"])

    def test_yaml_to_mdp_with_output_path(self):
        """Test converting YAML to MDP with output path."""
        doc = yaml_to_mdp(
            self.yaml_data,
            output_path=self.output_path
        )
        
        self.assertTrue(self.output_path.exists())
        
        # Load the saved document
        loaded_doc = Document.from_file(self.output_path)
        self.assertEqual(loaded_doc.title, "Test YAML Document")
        self.assertEqual(loaded_doc.author, "Test Author")
        self.assertEqual(loaded_doc.tags, ["yaml", "test", "converter"])

    def test_yaml_to_mdp_with_custom_metadata(self):
        """Test converting YAML to MDP with custom metadata."""
        doc = yaml_to_mdp(
            self.yaml_data,
            metadata={
                "title": "Custom Title",
                "author": "Custom Author",
                "tags": ["custom", "metadata"]
            }
        )
        
        self.assertEqual(doc.title, "Custom Title")
        self.assertEqual(doc.author, "Custom Author")
        self.assertEqual(doc.tags, ["custom", "metadata"])


class TestMarkdownConverter(unittest.TestCase):
    """Test cases for the Markdown converter."""

    def setUp(self):
        """Set up test fixtures."""
        self.markdown_with_frontmatter = """---
title: Test Markdown Document
author: Test Author
date: 2023-06-02
tags: [markdown, test, converter]
---

# Introduction

This is a test markdown document with frontmatter.

## Section 1

Content of section 1.

## Section 2

Content of section 2.

Tags: #markdown #test #converter
"""
        
        self.markdown_without_frontmatter = """# Test Markdown Document

This is a test markdown document without frontmatter.

## Section 1

Content of section 1.

## Section 2

Content of section 2.

Tags: #markdown #test #converter
"""
        
        # Create temporary files
        self.temp_file_with_fm = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
        self.temp_file_with_fm.write(self.markdown_with_frontmatter.encode('utf-8'))
        self.temp_file_with_fm.close()
        
        self.temp_file_without_fm = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
        self.temp_file_without_fm.write(self.markdown_without_frontmatter.encode('utf-8'))
        self.temp_file_without_fm.close()
        
        # Create a temporary output directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "output.mdp"

    def tearDown(self):
        """Tear down test fixtures."""
        os.unlink(self.temp_file_with_fm.name)
        os.unlink(self.temp_file_without_fm.name)
        self.temp_dir.cleanup()

    def test_markdown_with_frontmatter_to_mdp(self):
        """Test converting Markdown with frontmatter to MDP."""
        doc = markdown_to_mdp(self.markdown_with_frontmatter)
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "Test Markdown Document")
        self.assertEqual(doc.author, "Test Author")
        self.assertEqual(doc.metadata.get("created_at"), "2023-06-02")
        self.assertEqual(set(doc.tags), set(["markdown", "test", "converter"]))
        
        # Check source information
        self.assertEqual(doc.metadata.get("source", {}).get("type"), "markdown")
        self.assertIn("converter", doc.metadata.get("source", {}))
        self.assertIn("converted_at", doc.metadata.get("source", {}))

    def test_markdown_without_frontmatter_to_mdp(self):
        """Test converting Markdown without frontmatter to MDP."""
        doc = markdown_to_mdp(self.markdown_without_frontmatter)
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "Test Markdown Document")  # Extracted from heading
        self.assertEqual(set(doc.tags), set(["markdown", "test", "converter"]))  # Extracted from hashtags

    def test_markdown_file_to_mdp(self):
        """Test converting Markdown file to MDP."""
        doc = markdown_to_mdp(self.temp_file_with_fm.name)
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "Test Markdown Document")
        self.assertEqual(doc.author, "Test Author")
        self.assertEqual(set(doc.tags), set(["markdown", "test", "converter"]))

    def test_markdown_to_mdp_with_output_path(self):
        """Test converting Markdown to MDP with output path."""
        doc = markdown_to_mdp(
            self.markdown_with_frontmatter,
            output_path=self.output_path
        )
        
        self.assertTrue(self.output_path.exists())
        
        # Load the saved document
        loaded_doc = Document.from_file(self.output_path)
        self.assertEqual(loaded_doc.title, "Test Markdown Document")
        self.assertEqual(loaded_doc.author, "Test Author")
        self.assertEqual(set(loaded_doc.tags), set(["markdown", "test", "converter"]))

    def test_markdown_to_mdp_with_custom_metadata(self):
        """Test converting Markdown to MDP with custom metadata."""
        doc = markdown_to_mdp(
            self.markdown_with_frontmatter,
            metadata={
                "title": "Custom Title",
                "author": "Custom Author",
                "tags": ["custom", "metadata"]
            }
        )
        
        self.assertEqual(doc.title, "Custom Title")
        self.assertEqual(doc.author, "Custom Author")
        self.assertEqual(doc.tags, ["custom", "metadata"])

    def test_markdown_to_mdp_preserve_frontmatter(self):
        """Test converting Markdown to MDP with preserved frontmatter."""
        doc = markdown_to_mdp(
            self.markdown_with_frontmatter,
            preserve_frontmatter=True
        )
        
        # Check if frontmatter is preserved in content
        self.assertIn("---", doc.content)
        self.assertIn("title: Test Markdown Document", doc.content)
        
        # Parse the content to verify frontmatter is valid
        parsed = frontmatter.loads(doc.content)
        self.assertEqual(parsed.metadata.get("title"), "Test Markdown Document")
        self.assertEqual(parsed.metadata.get("author"), "Test Author")


@unittest.skipIf(not PDF_SUPPORT, "PDF support not available")
class TestPDFConverter(unittest.TestCase):
    """Test cases for the PDF converter."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary output directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "output.mdp"
        
        # Create a minimal PDF in memory for testing
        if PDF_SUPPORT:
            self.create_test_pdf()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
        if hasattr(self, 'temp_pdf_path') and self.temp_pdf_path.exists():
            self.temp_pdf_path.unlink()

    def create_test_pdf(self):
        """Create a minimal PDF for testing."""
        try:
            # Create a simple PDF with one page
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)  # Standard letter size
            
            # Add some metadata
            writer.add_metadata({
                "/Title": "Test PDF Document",
                "/Author": "Test Author",
                "/Subject": "PDF Testing",
                "/Keywords": "test,pdf,converter",
                "/CreationDate": "D:20230603120000",
            })
            
            # Save to a temporary file
            self.temp_pdf_path = Path(self.temp_dir.name) / "test.pdf"
            with open(self.temp_pdf_path, "wb") as f:
                writer.write(f)
            
            self.has_test_pdf = True
        except Exception as e:
            print(f"Failed to create test PDF: {e}")
            self.has_test_pdf = False

    def test_pdf_support_available(self):
        """Test that PDF support is available."""
        self.assertTrue(PDF_SUPPORT)
        
        # Import should succeed
        from datapack.converters import pdf_to_mdp
        self.assertIsNotNone(pdf_to_mdp)

    @unittest.skipIf(not hasattr(TestPDFConverter, 'has_test_pdf') or not TestPDFConverter.has_test_pdf, 
                    "Test PDF creation failed")
    def test_pdf_file_to_mdp(self):
        """Test converting PDF file to MDP."""
        doc = pdf_to_mdp(self.temp_pdf_path)
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "Test PDF Document")
        self.assertEqual(doc.author, "Test Author")
        
        # Check source information
        self.assertEqual(doc.metadata.get("source", {}).get("type"), "pdf")
        self.assertIn("converter", doc.metadata.get("source", {}))
        self.assertIn("converted_at", doc.metadata.get("source", {}))
        self.assertIn("page_count", doc.metadata.get("source", {}))
        self.assertEqual(doc.metadata.get("source", {}).get("page_count"), 1)

    @unittest.skipIf(not hasattr(TestPDFConverter, 'has_test_pdf') or not TestPDFConverter.has_test_pdf, 
                    "Test PDF creation failed")
    def test_pdf_to_mdp_with_custom_metadata(self):
        """Test converting PDF to MDP with custom metadata."""
        doc = pdf_to_mdp(
            self.temp_pdf_path,
            metadata={
                "title": "Custom PDF Title",
                "author": "Custom Author",
                "tags": ["custom", "pdf", "metadata"]
            }
        )
        
        self.assertEqual(doc.title, "Custom PDF Title")
        self.assertEqual(doc.author, "Custom Author")
        self.assertEqual(doc.tags, ["custom", "pdf", "metadata"])

    def test_pdf_bytes_to_mdp(self):
        """Test converting PDF bytes to MDP."""
        if not hasattr(self, 'temp_pdf_path') or not self.temp_pdf_path.exists():
            self.skipTest("Test PDF not available")
            
        # Read PDF as bytes
        with open(self.temp_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Convert bytes to MDP
        doc = pdf_to_mdp(
            pdf_bytes,
            metadata={"title": "PDF from Bytes"}
        )
        
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, "PDF from Bytes")


if __name__ == '__main__':
    unittest.main() 