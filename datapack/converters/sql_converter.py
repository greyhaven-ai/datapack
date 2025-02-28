"""
SQL to MDP converter.

This module provides functions to convert SQL files and query results to MDP format,
preserving structure and metadata.
"""

import os
import io
import re
import datetime
import csv
from typing import Dict, Any, Union, Optional, List, Tuple
from pathlib import Path

try:
    import sqlparse
    SQL_SUPPORT = True
except ImportError:
    SQL_SUPPORT = False

from mdp import Document, MDPFile
from mdp.metadata import create_metadata, generate_uuid, format_date
from .utils import normalize_metadata

def _check_sql_support():
    """
    Check if SQL parsing support is available.
    
    Raises:
        ImportError: If SQL parsing support is not available
    """
    if not SQL_SUPPORT:
        raise ImportError(
            "SQL parsing support requires additional dependencies. "
            "Install with 'pip install datapack[converters]' or 'pip install sqlparse'"
        )

def _extract_metadata_from_sql(sql_content: str) -> Dict[str, Any]:
    """
    Extract metadata from SQL content.
    
    Args:
        sql_content: The SQL content to extract metadata from
        
    Returns:
        A dictionary of metadata
    """
    _check_sql_support()
    
    metadata = {}
    
    # Parse SQL content
    statements = sqlparse.parse(sql_content)
    
    # Try to extract a title from comments
    title_pattern = re.compile(r'--\s*Title:\s*(.*?)(?:\n|$)', re.IGNORECASE)
    title_match = title_pattern.search(sql_content)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # Try to extract author from comments
    author_pattern = re.compile(r'--\s*Author:\s*(.*?)(?:\n|$)', re.IGNORECASE)
    author_match = author_pattern.search(sql_content)
    if author_match:
        metadata['author'] = author_match.group(1).strip()
    
    # Try to extract description from comments
    desc_pattern = re.compile(r'--\s*Description:\s*(.*?)(?:\n|$)', re.IGNORECASE)
    desc_match = desc_pattern.search(sql_content)
    if desc_match:
        metadata['description'] = desc_match.group(1).strip()
    
    # Try to extract date from comments
    date_pattern = re.compile(r'--\s*Date:\s*(.*?)(?:\n|$)', re.IGNORECASE)
    date_match = date_pattern.search(sql_content)
    if date_match:
        try:
            metadata['created_at'] = format_date(date_match.group(1).strip())
        except (ValueError, TypeError):
            # If parsing fails, keep as is
            metadata['created_at'] = date_match.group(1).strip()
    
    # Try to extract version from comments
    version_pattern = re.compile(r'--\s*Version:\s*(.*?)(?:\n|$)', re.IGNORECASE)
    version_match = version_pattern.search(sql_content)
    if version_match:
        metadata['version'] = version_match.group(1).strip()
    
    # Try to extract tags from comments
    tags_pattern = re.compile(r'--\s*Tags:\s*(.*?)(?:\n|$)', re.IGNORECASE)
    tags_match = tags_pattern.search(sql_content)
    if tags_match:
        tags_str = tags_match.group(1).strip()
        metadata['tags'] = [tag.strip() for tag in tags_str.split(',')]
    
    # Extract database objects
    tables = set()
    views = set()
    functions = set()
    
    for statement in statements:
        # Convert to lowercase for case-insensitive matching
        stmt_type = statement.get_type().lower() if statement.get_type() else ""
        
        if stmt_type == 'CREATE':
            # Check what's being created
            tokens = [token for token in statement.tokens if not token.is_whitespace]
            for i, token in enumerate(tokens):
                if token.normalized == 'TABLE' and i+1 < len(tokens):
                    # Extract table name
                    table_name = tokens[i+1].normalized
                    if table_name:
                        tables.add(table_name.strip('"\'`[]'))
                elif token.normalized == 'VIEW' and i+1 < len(tokens):
                    # Extract view name
                    view_name = tokens[i+1].normalized
                    if view_name:
                        views.add(view_name.strip('"\'`[]'))
                elif token.normalized == 'FUNCTION' and i+1 < len(tokens):
                    # Extract function name
                    func_name = tokens[i+1].normalized
                    if func_name:
                        functions.add(func_name.strip('"\'`[]'))
        
        elif stmt_type == 'SELECT':
            # Extract tables from FROM clause
            from_seen = False
            for token in statement.tokens:
                if token.normalized == 'FROM':
                    from_seen = True
                elif from_seen and token.ttype is None:  # Table name
                    # Extract table names from FROM clause
                    for identifier in token.get_identifiers():
                        tables.add(identifier.normalized.strip('"\'`[]'))
    
    # Add database objects to metadata
    if tables:
        metadata['tables'] = list(tables)
    if views:
        metadata['views'] = list(views)
    if functions:
        metadata['functions'] = list(functions)
    
    # Normalize metadata to conform to MDP standards
    return normalize_metadata(metadata)

def _format_sql(sql_content: str) -> str:
    """
    Format SQL content for better readability.
    
    Args:
        sql_content: The SQL content to format
        
    Returns:
        Formatted SQL content
    """
    _check_sql_support()
    
    # Parse and format SQL
    statements = sqlparse.parse(sql_content)
    formatted_statements = []
    
    for statement in statements:
        formatted = sqlparse.format(
            str(statement),
            reindent=True,
            keyword_case='upper',
            identifier_case='lower',
            indent_width=4
        )
        formatted_statements.append(formatted)
    
    return '\n\n'.join(formatted_statements)

def _sql_to_markdown(sql_content: str, format_sql: bool = True) -> str:
    """
    Convert SQL content to markdown.
    
    Args:
        sql_content: The SQL content to convert
        format_sql: Whether to format the SQL for better readability
        
    Returns:
        Markdown representation of the SQL content
    """
    _check_sql_support()
    
    content = []
    
    # Extract comments at the beginning
    comment_block = []
    for line in sql_content.split('\n'):
        line = line.strip()
        if line.startswith('--'):
            # Skip metadata comments that we've already extracted
            if not re.match(r'--\s*(Title|Author|Description|Date|Version|Tags):', line, re.IGNORECASE):
                comment_block.append(line[2:].strip())
        elif not line:
            # Empty line, continue collecting comments
            if comment_block:
                comment_block.append('')
        else:
            # Non-comment line, stop collecting
            break
    
    # Add comment block if found
    if comment_block:
        content.append("## Description\n")
        content.append('\n'.join(comment_block))
        content.append("\n")
    
    # Format SQL if requested
    if format_sql:
        formatted_sql = _format_sql(sql_content)
    else:
        formatted_sql = sql_content
    
    # Add SQL code block
    content.append("## SQL Code\n")
    content.append("```sql")
    content.append(formatted_sql)
    content.append("```\n")
    
    # Parse SQL to extract statements
    statements = sqlparse.parse(sql_content)
    
    # Add statement analysis
    if len(statements) > 1:
        content.append("## Statement Analysis\n")
        
        for i, statement in enumerate(statements, 1):
            stmt_type = statement.get_type()
            if stmt_type:
                content.append(f"### Statement {i}: {stmt_type}\n")
                content.append("```sql")
                content.append(str(statement))
                content.append("```\n")
    
    return '\n'.join(content)

def _query_results_to_markdown(results: List[Dict[str, Any]]) -> str:
    """
    Convert query results to markdown.
    
    Args:
        results: List of dictionaries representing query results
        
    Returns:
        Markdown representation of the query results
    """
    if not results:
        return "*No results*"
    
    # Get column names from the first row
    columns = list(results[0].keys())
    
    # Create markdown table
    table = []
    
    # Add header row
    table.append("| " + " | ".join(columns) + " |")
    
    # Add separator row
    table.append("| " + " | ".join(["---"] * len(columns)) + " |")
    
    # Add data rows
    for row in results:
        values = []
        for col in columns:
            value = row.get(col, "")
            # Format value for markdown table
            if value is None:
                value = "NULL"
            else:
                value = str(value).replace("|", "\\|")
            values.append(value)
        
        table.append("| " + " | ".join(values) + " |")
    
    return "\n".join(table)

def sql_to_mdp(
    sql_data: Union[str, Path, bytes, io.BytesIO], 
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    extract_metadata: bool = True,
    format_sql: bool = True,
    query_results: Optional[List[Dict[str, Any]]] = None
) -> Document:
    """
    Convert SQL data to an MDP document.
    
    Args:
        sql_data: SQL data as a string, file path, bytes, or BytesIO object
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to use (overrides extracted metadata)
        extract_metadata: Whether to extract metadata from the SQL
        format_sql: Whether to format the SQL for better readability
        query_results: Optional query results to include in the document
        
    Returns:
        An MDP Document object
        
    Raises:
        ImportError: If SQL parsing support is not available
        ValueError: If sql_data is invalid
    """
    _check_sql_support()
    
    # Load the SQL data
    if isinstance(sql_data, (str, Path)) and os.path.exists(sql_data):
        try:
            with open(sql_data, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read SQL file: {e}") from e
    elif isinstance(sql_data, bytes):
        try:
            sql_content = sql_data.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError("Failed to decode SQL data as UTF-8")
    elif isinstance(sql_data, io.BytesIO):
        try:
            sql_content = sql_data.read().decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError("Failed to decode SQL data as UTF-8")
    else:
        # Assume it's a string
        sql_content = sql_data
    
    # Extract metadata if requested
    doc_metadata = {}
    if extract_metadata:
        doc_metadata = _extract_metadata_from_sql(sql_content)
    
    # Override with provided metadata
    if metadata:
        # Normalize the provided metadata too
        normalized_metadata = normalize_metadata(metadata)
        doc_metadata.update(normalized_metadata)
    
    # Ensure required metadata
    if "title" not in doc_metadata:
        # Try to use filename if available
        if isinstance(sql_data, (str, Path)) and os.path.exists(sql_data):
            filename = os.path.basename(sql_data)
            base_name = os.path.splitext(filename)[0]
            doc_metadata["title"] = base_name.replace('_', ' ').replace('-', ' ').title()
        else:
            # Try to extract a title from the first statement
            statements = sqlparse.parse(sql_content)
            if statements:
                first_stmt = statements[0]
                stmt_type = first_stmt.get_type()
                if stmt_type:
                    doc_metadata["title"] = f"{stmt_type} Statement"
                else:
                    doc_metadata["title"] = "SQL Statement"
            else:
                doc_metadata["title"] = "SQL Document"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "sql",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.sql_converter"
    }
    
    # Convert SQL to markdown
    content = _sql_to_markdown(sql_content, format_sql)
    
    # Add query results if provided
    if query_results:
        content += "\n\n## Query Results\n\n"
        content += _query_results_to_markdown(query_results)
    
    # Create the document
    doc = Document.create(
        content=content,
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc

def query_results_to_mdp(
    results: List[Dict[str, Any]],
    query: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None
) -> Document:
    """
    Convert query results to an MDP document.
    
    Args:
        results: List of dictionaries representing query results
        query: Optional SQL query that produced the results
        output_path: Optional path to save the MDP file
        metadata: Optional metadata to include in the document
        title: Optional title for the document
        
    Returns:
        An MDP Document object
        
    Raises:
        ImportError: If SQL parsing support is not available
    """
    _check_sql_support()
    
    # Create content
    content = []
    
    # Add query if provided
    if query:
        content.append("## SQL Query\n")
        content.append("```sql")
        content.append(_format_sql(query))
        content.append("```\n")
    
    # Add results
    content.append("## Query Results\n")
    content.append(_query_results_to_markdown(results))
    
    # Prepare metadata
    doc_metadata = metadata or {}
    
    # Normalize the provided metadata
    doc_metadata = normalize_metadata(doc_metadata)
    
    # Set title
    if title:
        doc_metadata["title"] = title
    elif "title" not in doc_metadata:
        doc_metadata["title"] = "SQL Query Results"
    
    # Add source information
    doc_metadata["source"] = {
        "type": "sql_results",
        "converted_at": format_date(datetime.datetime.now()),
        "converter": "datapack.converters.sql_converter"
    }
    
    # Add result statistics
    doc_metadata["x_result_stats"] = {
        "row_count": len(results),
        "column_count": len(results[0].keys()) if results else 0
    }
    
    # Create the document
    doc = Document.create(
        content="\n".join(content),
        **doc_metadata
    )
    
    # Save if output path is provided
    if output_path:
        doc.save(output_path)
    
    return doc 