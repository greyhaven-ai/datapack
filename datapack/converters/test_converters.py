"""
Unit tests for the datapack.converters module.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from mdp import Document

from datapack.converters import json_to_mdp, xml_to_mdp, csv_to_mdp


class TestJsonConverter(unittest.TestCase):
    """Tests for the JSON to MDP converter."""
    
    def setUp(self):
        """Set up test data."""
        self.json_data = {
            "title": "Test JSON Document",
            "description": "A test document for JSON conversion",
            "author": "Test Author",
            "data": {
                "value1": 123,
                "value2": "test",
                "nested": {
                    "inner": "value"
                }
            }
        }
        
    def test_json_dict_conversion(self):
        """Test converting a JSON dictionary."""
        doc = json_to_mdp(self.json_data)
        
        # Check basic properties
        self.assertEqual(doc.title, "Test JSON Document")
        self.assertEqual(doc.author, "Test Author")
        self.assertIn("source", doc.metadata)
        self.assertEqual(doc.metadata["source"]["type"], "json")
        
        # Check content
        self.assertIn("# Test JSON Document", doc.content)
        self.assertIn("A test document for JSON conversion", doc.content)
        self.assertIn("## JSON Data", doc.content)
        
    def test_json_string_conversion(self):
        """Test converting a JSON string."""
        json_string = json.dumps(self.json_data)
        doc = json_to_mdp(json_string)
        
        # Check basic properties
        self.assertEqual(doc.title, "Test JSON Document")
        
    def test_json_file_conversion(self):
        """Test converting a JSON file."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            json.dump(self.json_data, f)
            temp_path = f.name
            
        try:
            doc = json_to_mdp(temp_path)
            
            # Check basic properties
            self.assertEqual(doc.title, "Test JSON Document")
            self.assertEqual(doc.author, "Test Author")
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_custom_metadata(self):
        """Test providing custom metadata."""
        doc = json_to_mdp(
            self.json_data,
            metadata={"title": "Custom Title", "tags": ["test", "custom"]},
            extract_metadata=True  # Still extract but override with custom
        )
        
        # Custom metadata should override extracted
        self.assertEqual(doc.title, "Custom Title")
        self.assertEqual(doc.metadata["tags"], ["test", "custom"])
        # But other extracted metadata should remain
        self.assertEqual(doc.author, "Test Author")


class TestXmlConverter(unittest.TestCase):
    """Tests for the XML to MDP converter."""
    
    def setUp(self):
        """Set up test data."""
        self.xml_data = """
        <document>
            <title>Test XML Document</title>
            <metadata>
                <author>Test Author</author>
                <created>2023-01-01</created>
            </metadata>
            <content>
                <section>
                    <heading>Introduction</heading>
                    <text>This is the introduction.</text>
                </section>
            </content>
        </document>
        """
        
    def test_xml_string_conversion(self):
        """Test converting an XML string."""
        doc = xml_to_mdp(self.xml_data)
        
        # Check basic properties
        self.assertEqual(doc.title, "Test XML Document")
        self.assertIn("source", doc.metadata)
        self.assertEqual(doc.metadata["source"]["type"], "xml")
        
        # Check content
        self.assertIn("# Test XML Document", doc.content)
        self.assertIn("## XML Structure", doc.content)
        
    def test_xml_file_conversion(self):
        """Test converting an XML file."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False, mode='w') as f:
            f.write(self.xml_data)
            temp_path = f.name
            
        try:
            doc = xml_to_mdp(temp_path)
            
            # Check basic properties
            self.assertEqual(doc.title, "Test XML Document")
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_custom_options(self):
        """Test providing custom options."""
        doc = xml_to_mdp(
            self.xml_data,
            max_depth=2,
            include_attributes=False
        )
        
        # Check that content is affected by options
        self.assertIn("# Test XML Document", doc.content)
        

class TestCsvConverter(unittest.TestCase):
    """Tests for the CSV to MDP converter."""
    
    def setUp(self):
        """Set up test data."""
        self.csv_data = """
        name,age,email
        John Doe,32,john@example.com
        Jane Smith,28,jane@example.com
        """
        
    def test_csv_string_conversion(self):
        """Test converting a CSV string."""
        doc = csv_to_mdp(self.csv_data.strip())
        
        # Check basic properties
        self.assertIn("CSV Data", doc.title)  # Generated title
        self.assertIn("source", doc.metadata)
        self.assertEqual(doc.metadata["source"]["type"], "csv")
        
        # Check content
        self.assertIn("## Data Table", doc.content)
        self.assertIn("name", doc.content)
        self.assertIn("John Doe", doc.content)
        
    def test_csv_file_conversion(self):
        """Test converting a CSV file."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write(self.csv_data)
            temp_path = f.name
            
        try:
            doc = csv_to_mdp(temp_path)
            
            # Check basic content
            self.assertIn("## Data Table", doc.content)
            self.assertIn("name", doc.content)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_stats_generation(self):
        """Test generating statistics for CSV data."""
        numeric_csv = """
        name,age,score
        John,32,85
        Jane,28,92
        Bob,45,78
        """
        
        doc = csv_to_mdp(numeric_csv.strip(), include_stats=True)
        
        # Check for stats in the content
        self.assertIn("## Summary Statistics", doc.content)
        self.assertIn("Total rows", doc.content)
        self.assertIn("Numeric Column", doc.content)
        
    def test_custom_options(self):
        """Test providing custom options."""
        doc = csv_to_mdp(
            self.csv_data.strip(),
            metadata={"title": "Custom CSV Title"},
            max_rows=1,  # Show only one row
            has_header=True
        )
        
        # Check custom title
        self.assertEqual(doc.title, "Custom CSV Title")
        
        # Should include header and just one data row
        self.assertIn("name", doc.content)
        self.assertIn("John Doe", doc.content)


if __name__ == "__main__":
    unittest.main() 