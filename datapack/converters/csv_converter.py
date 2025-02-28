"""
CSV to MDP converter.

This module provides functions to convert CSV data to MDP format,
preserving structure and metadata.
"""

import csv
import os
import io
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path
import datetime

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid

def _detect_csv_dialect(csv_data: Union[str, Path]) -> csv.Dialect:
    """
    Detect the dialect of a CSV file.
    
    Args:
        csv_data: CSV data as a string or file path
        
    Returns:
        A csv.Dialect object
        
    Raises:
        ValueError: If csv_data is invalid
    """
    sample = ""
    
    # Get a sample of the CSV data
    if isinstance(csv_data, Path) or (isinstance(csv_data, str) and os.path.exists(csv_data)):
        with open(csv_data, 'r', newline='', encoding='utf-8') as f:
            sample = f.read(4096)  # Read a sample for dialect detection
    else:
        sample = csv_data[:4096] if len(csv_data) > 4096 else csv_data
    
    try:
        dialect = csv.Sniffer().sniff(sample)
        return dialect
    except csv.Error:
        # If sniffer fails, return excel dialect as default
        return csv.excel

def _extract_metadata_from_csv(
    headers: List[str], 
    first_row: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extract metadata from CSV headers and first row.
    
    Args:
        headers: The CSV headers
        first_row: The first data row (optional)
        
    Returns:
        A dictionary of metadata
    """
    metadata = {}
    
    # Common metadata headers
    metadata_fields = {
        "title": ["title", "name", "heading", "document title"],
        "description": ["description", "desc", "summary", "about"],
        "author": ["author", "creator", "owner", "created by"],
        "created_at": ["created_at", "created", "creation date", "date created"],
        "updated_at": ["updated_at", "updated", "last modified", "modified"],
        "version": ["version", "ver", "document version"],
        "tags": ["tags", "categories", "keywords"]
    }
    
    # Look for metadata in headers
    for i, header in enumerate(headers):
        header_lower = header.lower()
        
        for meta_key, possible_keys in metadata_fields.items():
            if any(key.lower() == header_lower for key in possible_keys):
                if first_row and i < len(first_row) and first_row[i]:
                    # Get the value from the first row
                    metadata[meta_key] = first_row[i]
                break
    
    # If no title found, create one based on the headers
    if "title" not in metadata:
        if len(headers) <= 5:
            # For small tables, use all headers
            metadata["title"] = f"CSV Data: {', '.join(headers)}"
        else:
            # For larger tables, use first 3 and count
            metadata["title"] = f"CSV Data: {', '.join(headers[:3])} and {len(headers)-3} more columns"
    
    # Format dates if needed
    for date_field in ["created_at", "updated_at"]:
        if date_field in metadata and isinstance(metadata[date_field], str):
            try:
                # Simple attempt to parse date formats
                date_formats = [
                    "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", 
                    "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"
                ]
                
                for fmt in date_formats:
                    try:
                        date_obj = datetime.datetime.strptime(metadata[date_field], fmt)
                        metadata[date_field] = date_obj.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
            except (ValueError, TypeError):
                # If parsing fails, keep as is
                pass
    
    return metadata

def _csv_to_markdown_table(
    headers: List[str], 
    rows: List[List[str]], 
    max_rows: int = 100
) -> str:
    """
    Convert CSV data to a markdown table.
    
    Args:
        headers: The CSV headers
        rows: The CSV data rows
        max_rows: Maximum number of rows to include
        
    Returns:
        A markdown table as a string
    """
    result = []
    
    # Add headers
    result.append("| " + " | ".join(str(h) for h in headers) + " |")
    
    # Add separator
    result.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    # Add rows (up to max_rows)
    for i, row in enumerate(rows):
        if i >= max_rows:
            result.append(f"\n*Table truncated. Showing {max_rows} of {len(rows)} rows.*")
            break
            
        # Ensure row has same length as headers
        padded_row = list(row)
        while len(padded_row) < len(headers):
            padded_row.append("")
            
        # Escape pipe characters in cell values
        escaped_row = [str(cell).replace("|", "\\|") for cell in padded_row]
        
        result.append("| " + " | ".join(escaped_row) + " |")
    
    return "\n".join(result)

def _csv_to_summary_stats(
    headers: List[str], 
    rows: List[List[Any]]
) -> str:
    """
    Generate summary statistics for CSV data.
    
    Args:
        headers: The CSV headers
        rows: The CSV data rows
        
    Returns:
        A markdown string with summary statistics
    """
    result = ["## Summary Statistics\n"]
    
    # Basic stats
    result.append(f"- **Total rows**: {len(rows)}")
    result.append(f"- **Total columns**: {len(headers)}")
    
    # Try to identify numeric columns and calculate stats
    for i, header in enumerate(headers):
        # Extract values for this column
        values = [row[i] for row in rows if i < len(row)]
        
        # Skip empty columns
        if not values:
            continue
            
        # Check if column is numeric
        numeric_values = []
        for v in values:
            try:
                if v and v.strip():  # Skip empty values
                    numeric_values.append(float(v))
            except (ValueError, TypeError):
                pass
        
        # If at least 50% of values are numeric, calculate stats
        if len(numeric_values) >= len(values) * 0.5:
            if numeric_values:
                result.append(f"\n### {header} (Numeric Column)")
                result.append(f"- **Count**: {len(numeric_values)}")
                result.append(f"- **Min**: {min(numeric_values)}")
                result.append(f"- **Max**: {max(numeric_values)}")
                result.append(f"- **Average**: {sum(numeric_values) / len(numeric_values):.2f}")
                
                # Calculate median
                sorted_values = sorted(numeric_values)
                mid = len(sorted_values) // 2
                median = sorted_values[mid] if len(sorted_values) % 2 == 1 else (sorted_values[mid-1] + sorted_values[mid]) / 2
                result.append(f"- **Median**: {median:.2f}")
    
    return "\n".join(result)

def csv_to_mdp(
    csv_data: Union[str, Path], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    include_stats: bool = True,
    max_rows: int = 100,
    delimiter: Optional[str] = None,
    has_header: bool = True,
    encoding: str = 'utf-8'
) -> Document:
    """
    Convert CSV data to an MDP document.
    
    Args:
        csv_data: CSV data as a string or file path
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the CSV
        include_stats: Whether to include summary statistics
        max_rows: Maximum number of rows to display in the table
        delimiter: CSV delimiter (auto-detected if None)
        has_header: Whether the CSV has a header row
        encoding: File encoding
        
    Returns:
        An MDP Document object
        
    Raises:
        ValueError: If csv_data is invalid
    """
    # Open CSV file or use string data
    rows = []
    dialect = None
    headers = []
    
    try:
        if isinstance(csv_data, Path) or (isinstance(csv_data, str) and os.path.exists(csv_data)):
            # Detect dialect first if delimiter not specified
            if delimiter is None:
                dialect = _detect_csv_dialect(csv_data)
            
            with open(csv_data, 'r', newline='', encoding=encoding) as f:
                if delimiter:
                    reader = csv.reader(f, delimiter=delimiter)
                elif dialect:
                    reader = csv.reader(f, dialect=dialect)
                else:
                    reader = csv.reader(f)
                
                rows = list(reader)
        else:
            # It's a string with CSV content
            if delimiter is None:
                dialect = _detect_csv_dialect(csv_data)
            
            f = io.StringIO(csv_data)
            if delimiter:
                reader = csv.reader(f, delimiter=delimiter)
            elif dialect:
                reader = csv.reader(f, dialect=dialect)
            else:
                reader = csv.reader(f)
                
            rows = list(reader)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV data: {e}") from e
    
    if not rows:
        raise ValueError("No data found in CSV")
    
    # Extract headers and data rows
    if has_header:
        headers = rows[0]
        data_rows = rows[1:]
    else:
        # Create generic headers (Column A, Column B, etc.)
        if rows:
            max_cols = max(len(row) for row in rows)
            headers = [f"Column {chr(65 + i)}" for i in range(min(max_cols, 26))]
            # Add Column AA, Column AB etc. for more than 26 columns
            if max_cols > 26:
                headers.extend([f"Column {chr(65 + i // 26)}{chr(65 + i % 26)}" for i in range(26, max_cols)])
        data_rows = rows
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata and has_header and len(data_rows) > 0:
        doc_metadata = _extract_metadata_from_csv(headers, data_rows[0])
    
    # Override with provided metadata
    if metadata:
        doc_metadata.update(metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        doc_metadata["title"] = "Converted CSV Document"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "csv",
        "converted_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "converter": "datapack.converters.csv_converter",
        "rows": len(data_rows),
        "columns": len(headers)
    }
    
    # Create markdown content
    content = f"# {doc_metadata.get('title')}\n\n"
    if "description" in doc_metadata:
        content += f"{doc_metadata['description']}\n\n"
    
    # Add table
    content += "## Data Table\n\n"
    content += _csv_to_markdown_table(headers, data_rows, max_rows)
    content += "\n\n"
    
    # Add summary statistics if requested
    if include_stats:
        content += _csv_to_summary_stats(headers, data_rows)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 