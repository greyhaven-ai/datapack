#!/usr/bin/env python3
"""
Example script demonstrating advanced metadata features in MDP files:
- Date format standardization
- Required fields
- Custom field namespaces
"""

import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datapack.mdp import MDPFile, write_mdp, read_mdp
from datapack.mdp.metadata import (
    create_custom_field,
    format_date,
    get_today_date,
    is_custom_field,
    validate_metadata
)


def demonstrate_required_fields():
    """Demonstrate required fields validation."""
    print("\n=== Required Fields ===")
    
    # This will fail because title is required
    try:
        metadata = {
            # Missing title
            "version": "1.0.0",
            "type": "document",
            "description": "This document is missing a title"
        }
        validate_metadata(metadata)
        print("Validation succeeded (unexpected)")
    except ValueError as e:
        print(f"Validation failed as expected: {e}")
    
    # This will succeed because all required fields are present
    try:
        metadata = {
            "title": "Document with Required Fields",
            "version": "1.0.0",
            "type": "document",
            "description": "This document has all required fields"
        }
        validate_metadata(metadata)
        print("Validation succeeded as expected")
    except ValueError as e:
        print(f"Validation failed (unexpected): {e}")


def demonstrate_date_format():
    """Demonstrate date format standardization."""
    print("\n=== Date Format Standardization ===")
    
    # Get today's date
    today = get_today_date()
    print(f"Today's date in standard format: {today}")
    
    # Format different date representations
    date_examples = [
        date(2023, 5, 15),                  # date object
        datetime(2023, 5, 15, 12, 30, 0),   # datetime object
        "2023-05-15",                       # ISO format (already correct)
        "2023/05/15",                       # Alternative format 1
        "15-05-2023",                       # Alternative format 2
        "05/15/2023",                       # Alternative format 3
        "May 15, 2023"                      # Alternative format 4
    ]
    
    print("Formatting different date representations:")
    for date_example in date_examples:
        try:
            formatted = format_date(date_example)
            print(f"  {date_example} -> {formatted}")
        except ValueError as e:
            print(f"  {date_example} -> Error: {e}")
    
    # Demonstrate validation of date fields
    print("\nValidating date fields:")
    
    # Valid date format
    try:
        metadata = {
            "title": "Document with Valid Date",
            "version": "1.0.0",
            "type": "document",
            "created_at": "2023-05-15"
        }
        validate_metadata(metadata)
        print("  Valid date format validated successfully")
    except ValueError as e:
        print(f"  Validation failed (unexpected): {e}")
    
    # Invalid date format
    try:
        metadata = {
            "title": "Document with Invalid Date",
            "version": "1.0.0",
            "type": "document",
            "created_at": "15/05/2023"  # Wrong format
        }
        validate_metadata(metadata)
        print("  Invalid date format validated (unexpected)")
    except ValueError as e:
        print(f"  Validation failed as expected: {e}")


def demonstrate_custom_fields():
    """Demonstrate custom field namespaces."""
    print("\n=== Custom Field Namespaces ===")
    
    # Create custom fields
    priority_field, priority_value = create_custom_field("priority", "high")
    status_field, status_value = create_custom_field("workflow_status", "in_review")
    
    print(f"Created custom fields:")
    print(f"  {priority_field}: {priority_value}")
    print(f"  {status_field}: {status_value}")
    
    # Check if fields are custom
    fields_to_check = [
        "title",
        "x_priority",
        "priority",
        "x_custom"
    ]
    
    print("\nChecking if fields are custom:")
    for field in fields_to_check:
        print(f"  {field}: {'custom' if is_custom_field(field) else 'standard'}")
    
    # Create and save a document with custom fields
    metadata = {
        "title": "Document with Custom Fields",
        "version": "1.0.0",
        "type": "document",
        "description": "This document demonstrates custom metadata fields",
        "created_at": get_today_date(),
        priority_field: priority_value,
        status_field: status_value,
        "x_review_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "x_reviewers": ["Alice", "Bob", "Charlie"]
    }
    
    content = """# Document with Custom Fields

This document demonstrates the use of custom metadata fields in MDP files.

## Custom Fields Used

- **x_priority**: Indicates the priority level of the document
- **x_workflow_status**: Indicates the current status in the workflow
- **x_review_date**: When the document should be reviewed
- **x_reviewers**: List of people who should review the document
"""
    
    # Create the examples directory if it doesn't exist
    examples_dir = Path(__file__).parent
    output_path = examples_dir / "custom_fields_example.mdp"
    
    # Write the MDP file
    mdp_file = write_mdp(output_path, metadata, content)
    
    print(f"\nCreated MDP file with custom fields at: {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
    
    # Read back and display metadata
    read_file = read_mdp(output_path)
    
    print("\nMetadata in the created file:")
    
    # Display standard fields
    print("  Standard fields:")
    for field in ["title", "version", "type", "created_at"]:
        print(f"    - {field}: {read_file.metadata[field]}")
    
    # Display custom fields
    print("  Custom fields:")
    custom_fields = [field for field in read_file.metadata if is_custom_field(field)]
    for field in custom_fields:
        print(f"    - {field}: {read_file.metadata[field]}")


def main():
    """Main function demonstrating advanced metadata features."""
    print("=== Advanced MDP Metadata Features ===")
    
    demonstrate_required_fields()
    demonstrate_date_format()
    demonstrate_custom_fields()
    
    print("\nAll demonstrations completed successfully!")


if __name__ == "__main__":
    main() 