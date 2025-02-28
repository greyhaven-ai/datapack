"""
Development workflows for MDP documents.

This module provides functions for integrating MDP documents with
software development workflows.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from mdp.document import Document
from mdp.utils import find_mdp_files, extract_metadata_from_content


def sync_codebase_docs(
    code_directory: Union[str, Path],
    docs_directory: Union[str, Path],
    file_patterns: List[str] = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs"],
    language_mapping: Optional[Dict[str, str]] = None,
    recursive: bool = True,
    dry_run: bool = False
) -> List[Document]:
    """
    Synchronize code documentation with MDP files.
    
    This function scans source code files for documentation blocks (docstrings,
    comments) and either creates new MDP documentation files or updates existing
    ones with the code documentation.
    
    Args:
        code_directory: Directory containing source code
        docs_directory: Directory where MDP docs should be stored
        file_patterns: File patterns to match source files
        language_mapping: Custom mapping of file extensions to language names
        recursive: Whether to scan directories recursively
        dry_run: If True, don't actually write files
        
    Returns:
        List of Document objects that were created or updated
    """
    # Ensure directories are Path objects
    code_dir = Path(code_directory)
    docs_dir = Path(docs_directory)
    
    # Default language mapping
    if language_mapping is None:
        language_mapping = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".c": "C",
            ".cpp": "C++",
            ".h": "C/C++ Header",
            ".cs": "C#",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala"
        }
    
    # Find source files
    source_files = []
    for pattern in file_patterns:
        if recursive:
            # Use glob with **/ for recursive search
            source_files.extend(list(code_dir.glob(f"**/{pattern}")))
        else:
            # Use glob without **/ for non-recursive search
            source_files.extend(list(code_dir.glob(pattern)))
    
    # Find existing MDP files
    existing_mdp_files = find_mdp_files(docs_dir, recursive=True)
    existing_mdp_dict = {}
    for path in existing_mdp_files:
        try:
            doc = Document.from_file(path)
            # Use source_file metadata to map to original source
            if "source_file" in doc.metadata:
                source_path = doc.metadata["source_file"]
                existing_mdp_dict[source_path] = doc
        except Exception as e:
            print(f"Warning: Could not load MDP file {path}: {e}")
    
    # Process each source file
    created_or_updated = []
    
    for source_path in source_files:
        # Get relative path for identification
        rel_path = source_path.relative_to(code_dir)
        rel_path_str = str(rel_path).replace("\\", "/")  # Normalize path separators
        
        # Determine language from file extension
        file_ext = source_path.suffix.lower()
        language = language_mapping.get(file_ext, "Unknown")
        
        # Read source file content
        with open(source_path, "r", encoding="utf-8", errors="replace") as f:
            source_content = f.read()
        
        # Extract documentation based on language
        doc_blocks = extract_docs_from_source(source_content, language)
        
        if not doc_blocks:
            # Skip files with no documentation
            continue
        
        # Combine doc blocks into MDP content
        mdp_content = f"# {source_path.stem}\n\n"
        for title, content in doc_blocks:
            if title:
                mdp_content += f"## {title}\n\n"
            mdp_content += f"{content}\n\n"
        
        # Check if MDP file already exists
        if rel_path_str in existing_mdp_dict:
            # Update existing document
            doc = existing_mdp_dict[rel_path_str]
            doc.content = mdp_content
            doc.metadata["updated_at"] = Document.get_today_date()
        else:
            # Create new document
            doc_path = docs_dir / rel_path.with_suffix(".mdp")
            
            # Create with auto-metadata
            doc = Document.create_with_auto_metadata(
                content=mdp_content,
                auto_title=True,
                auto_tags=True,
                auto_summary=True,
                title=source_path.stem,
                language=language,
                source_file=rel_path_str
            )
            doc._mdp_file.path = doc_path
        
        # Save document unless this is a dry run
        if not dry_run:
            # Ensure parent directory exists
            if doc._mdp_file.path:
                os.makedirs(doc._mdp_file.path.parent, exist_ok=True)
                doc.save()
        
        created_or_updated.append(doc)
    
    return created_or_updated


def extract_docs_from_source(source_content: str, language: str) -> List[tuple]:
    """
    Extract documentation from source code.
    
    Args:
        source_content: Source code as string
        language: Programming language
        
    Returns:
        List of (title, content) tuples
    """
    doc_blocks = []
    
    if language == "Python":
        # Extract docstrings
        docstring_pattern = r'"""(.*?)"""'
        matches = re.finditer(docstring_pattern, source_content, re.DOTALL)
        
        for match in matches:
            docstring = match.group(1).strip()
            # Try to determine if this is a class or function docstring
            function_match = re.search(r'def\s+(\w+)\s*\(.*?\):', source_content[:match.start()])
            class_match = re.search(r'class\s+(\w+)[\s\(]', source_content[:match.start()])
            
            title = None
            if function_match and function_match.end() > (match.start() - 50):
                title = f"Function: {function_match.group(1)}"
            elif class_match and class_match.end() > (match.start() - 50):
                title = f"Class: {class_match.group(1)}"
            
            doc_blocks.append((title, docstring))
    
    elif language in ["JavaScript", "TypeScript"]:
        # Extract JSDoc comments
        jsdoc_pattern = r'/\*\*(.*?)\*/'
        matches = re.finditer(jsdoc_pattern, source_content, re.DOTALL)
        
        for match in matches:
            jsdoc = match.group(1).strip()
            # Clean up asterisks at start of lines
            jsdoc = re.sub(r'^\s*\*\s?', '', jsdoc, flags=re.MULTILINE)
            
            # Try to determine what this documents
            function_match = re.search(r'function\s+(\w+)\s*\(', source_content[match.end():match.end()+100])
            method_match = re.search(r'(\w+)\s*\([^)]*\)\s*{', source_content[match.end():match.end()+100])
            class_match = re.search(r'class\s+(\w+)', source_content[match.end():match.end()+100])
            
            title = None
            if function_match:
                title = f"Function: {function_match.group(1)}"
            elif class_match:
                title = f"Class: {class_match.group(1)}"
            elif method_match:
                title = f"Method: {method_match.group(1)}"
            
            doc_blocks.append((title, jsdoc))
    
    # Add more language-specific extractors as needed
    
    return doc_blocks


def generate_api_docs(
    code_directory: Union[str, Path],
    output_file: Union[str, Path],
    module_name: str,
    include_patterns: List[str] = ["*.py"],
    exclude_patterns: List[str] = ["__pycache__", "*.pyc", "test_*", "*_test.py"],
    recursive: bool = True
) -> Document:
    """
    Generate API documentation for a Python module.
    
    Args:
        code_directory: Directory containing Python module
        output_file: Path to output MDP file
        module_name: Name of the module being documented
        include_patterns: File patterns to include
        exclude_patterns: File patterns to exclude
        recursive: Whether to scan directories recursively
        
    Returns:
        Document object for the generated API documentation
    """
    code_dir = Path(code_directory)
    
    # Find Python files
    python_files = []
    for pattern in include_patterns:
        if recursive:
            python_files.extend(list(code_dir.glob(f"**/{pattern}")))
        else:
            python_files.extend(list(code_dir.glob(pattern)))
    
    # Apply exclusions
    for pattern in exclude_patterns:
        python_files = [f for f in python_files if not f.match(pattern) and pattern not in str(f)]
    
    # Sort files for consistent output
    python_files.sort()
    
    # Generate API documentation
    api_content = f"# {module_name} API Reference\n\n"
    api_content += f"This document provides reference documentation for the {module_name} module.\n\n"
    
    for py_file in python_files:
        rel_path = py_file.relative_to(code_dir)
        module_path = str(rel_path).replace("/", ".").replace("\\", ".").replace(".py", "")
        
        api_content += f"## {module_path}\n\n"
        
        # Read file and extract classes and functions
        with open(py_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)(?:\s*\([^)]*\))?:'
        class_matches = re.finditer(class_pattern, content)
        
        for match in class_matches:
            class_name = match.group(1)
            api_content += f"### class {class_name}\n\n"
            
            # Try to find class docstring
            class_docstring_match = re.search(
                r'class\s+' + re.escape(class_name) + r'(?:\s*\([^)]*\))?:\s*\n\s*"""(.*?)"""',
                content,
                re.DOTALL
            )
            
            if class_docstring_match:
                docstring = class_docstring_match.group(1).strip()
                api_content += f"{docstring}\n\n"
            
            # Extract methods
            method_pattern = r'def\s+(\w+)\s*\(self(?:,[^)]*|)?\):'
            method_section = content[match.end():]
            next_class = re.search(class_pattern, method_section)
            if next_class:
                method_section = method_section[:next_class.start()]
                
            method_matches = re.finditer(method_pattern, method_section)
            
            for method_match in method_matches:
                method_name = method_match.group(1)
                if method_name.startswith('_') and not method_name.startswith('__'):
                    # Skip private methods
                    continue
                    
                api_content += f"#### {method_name}()\n\n"
                
                # Try to find method docstring
                method_docstring_match = re.search(
                    r'def\s+' + re.escape(method_name) + r'\s*\(.*?\):\s*\n\s*"""(.*?)"""',
                    method_section,
                    re.DOTALL
                )
                
                if method_docstring_match:
                    docstring = method_docstring_match.group(1).strip()
                    api_content += f"{docstring}\n\n"
        
        # Extract standalone functions
        function_pattern = r'def\s+(\w+)\s*\((?!self).*?\):'
        func_matches = re.finditer(function_pattern, content)
        
        for match in func_matches:
            func_name = match.group(1)
            if func_name.startswith('_'):
                # Skip private functions
                continue
                
            api_content += f"### function {func_name}()\n\n"
            
            # Try to find function docstring
            func_docstring_match = re.search(
                r'def\s+' + re.escape(func_name) + r'\s*\(.*?\):\s*\n\s*"""(.*?)"""',
                content,
                re.DOTALL
            )
            
            if func_docstring_match:
                docstring = func_docstring_match.group(1).strip()
                api_content += f"{docstring}\n\n"
    
    # Create document with auto-metadata
    doc = Document.create_with_auto_metadata(
        content=api_content,
        title=f"{module_name} API Reference",
        doc_type="api_reference",
        module=module_name
    )
    
    # Save document
    doc._mdp_file.path = Path(output_file)
    os.makedirs(doc._mdp_file.path.parent, exist_ok=True)
    doc.save()
    
    return doc 