"""
Tests for metadata extraction functionality.
"""

import unittest
from mdp.utils import extract_metadata_from_content
from mdp.document import Document


class TestMetadataExtraction(unittest.TestCase):
    """Test cases for metadata extraction functionality."""
    
    def test_extract_title(self):
        """Test title extraction from content."""
        content = """# Test Document
        
        This is a test document with some content.
        """
        
        metadata = extract_metadata_from_content(
            content=content,
            extract_title=True,
            extract_tags=False,
            extract_summary=False
        )
        
        self.assertIn("title", metadata)
        self.assertEqual(metadata["title"], "Test Document")
    
    def test_extract_tags(self):
        """Test tag extraction from content."""
        content = """# Test Document
        
        This is a test document about Python programming. It discusses
        code, testing, and documentation techniques for Python projects.
        """
        
        metadata = extract_metadata_from_content(
            content=content,
            extract_title=False,
            extract_tags=True,
            extract_summary=False
        )
        
        self.assertIn("tags", metadata)
        self.assertIsInstance(metadata["tags"], list)
        self.assertTrue(len(metadata["tags"]) > 0)
        
        # Common words in the content should be in tags
        common_words = ["python", "document", "code", "testing"]
        found = False
        for tag in metadata["tags"]:
            if tag in common_words:
                found = True
                break
        
        self.assertTrue(found, f"None of {common_words} found in {metadata['tags']}")
    
    def test_extract_summary(self):
        """Test summary extraction from content."""
        content = """# Test Document
        
        This is the first paragraph that should be used as a summary.
        
        This is a second paragraph that should not be included in the summary.
        """
        
        metadata = extract_metadata_from_content(
            content=content,
            extract_title=False,
            extract_tags=False,
            extract_summary=True
        )
        
        self.assertIn("description", metadata)
        self.assertIn("first paragraph", metadata["description"])
        self.assertNotIn("second paragraph", metadata["description"])
    
    def test_document_auto_metadata(self):
        """Test Document.create_with_auto_metadata method."""
        content = """# Auto Document
        
        This is a test of automatic metadata extraction in the Document class.
        It should extract the title, tags, and a summary from this content.
        """
        
        doc = Document.create_with_auto_metadata(
            content=content,
            auto_title=True,
            auto_tags=True,
            auto_summary=True
        )
        
        self.assertEqual(doc.title, "Auto Document")
        self.assertTrue(len(doc.tags) > 0)
        self.assertIn("description", doc.metadata)
    
    def test_auto_enhance_metadata(self):
        """Test Document.auto_enhance_metadata method."""
        # Create a document with minimal metadata
        doc = Document.create(
            title="Basic Document",
            content="""# Enhanced Document
            
            This document will have its metadata enhanced automatically.
            We're testing the auto_enhance_metadata method which should
            add tags and a description without changing the original title.
            """
        )
        
        # Initial state
        self.assertEqual(doc.title, "Basic Document")
        self.assertEqual(doc.tags, [])
        self.assertNotIn("description", doc.metadata)
        
        # Enhance metadata
        doc.auto_enhance_metadata(
            update_title=False,  # Don't update title
            update_tags=True,
            update_summary=True
        )
        
        # After enhancement
        self.assertEqual(doc.title, "Basic Document")  # Title unchanged
        self.assertTrue(len(doc.tags) > 0)  # Tags added
        self.assertIn("description", doc.metadata)  # Description added


if __name__ == "__main__":
    unittest.main() 