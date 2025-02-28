"""
Release workflows for MDP documents.

This module provides functions for generating release documentation
such as release notes and changelogs from MDP documents.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Set

from mdp.document import Document
from mdp.collection import Collection
from mdp.utils import find_mdp_files


def create_release_notes(
    version: str,
    output_file: Union[str, Path],
    issue_tracker_url: Optional[str] = None,
    source_directory: Optional[Union[str, Path]] = None,
    git_log_range: Optional[str] = None,
    commit_categories: Optional[Dict[str, List[str]]] = None,
    include_contributors: bool = True
) -> Document:
    """
    Create release notes as an MDP document.
    
    This function generates formatted release notes based on git commit history
    and/or issue tracker data.
    
    Args:
        version: Version string (e.g., "1.0.0")
        output_file: Path to save the release notes document
        issue_tracker_url: URL to the issue tracker (optional)
        source_directory: Source code directory (for git operations)
        git_log_range: Git log range (e.g., "v0.9.0..HEAD")
        commit_categories: Dict mapping categories to lists of keywords
        include_contributors: Whether to include contributor list
        
    Returns:
        Document object for the generated release notes
    """
    # Use current date as release date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Set up default commit categories if not provided
    if commit_categories is None:
        commit_categories = {
            "Features": ["feat", "feature", "add", "new"],
            "Bug Fixes": ["fix", "bug", "issue", "resolve"],
            "Documentation": ["doc", "docs", "documentation"],
            "Performance": ["perf", "performance", "optimize", "speed"],
            "Refactoring": ["refactor", "refactoring", "clean", "cleanup"],
            "Testing": ["test", "tests", "testing"],
            "Builds": ["build", "ci", "cd", "pipeline"],
            "Dependencies": ["dep", "deps", "dependency", "dependencies", "upgrade"]
        }
    
    # Initialize the release notes content
    content = f"# Release Notes - Version {version}\n\n"
    content += f"Released on: {today}\n\n"
    
    # Get git commit history if requested
    commits_by_category = {}
    contributors = set()
    
    if source_directory and git_log_range:
        import subprocess
        
        # Change to source directory
        cwd = os.getcwd()
        os.chdir(Path(source_directory))
        
        try:
            # Get git log in a parseable format
            cmd = [
                "git", "log", 
                "--pretty=format:%h|%an|%ae|%s", 
                git_log_range
            ]
            
            git_log = subprocess.check_output(cmd, text=True)
            
            # Process each commit
            for line in git_log.splitlines():
                parts = line.split("|", 3)
                if len(parts) < 4:
                    continue
                    
                commit_hash, author_name, author_email, message = parts
                
                # Add to contributors
                if include_contributors:
                    contributors.add(author_name)
                
                # Categorize the commit
                categorized = False
                for category, keywords in commit_categories.items():
                    # Match against commit message prefixes and keywords
                    for keyword in keywords:
                        # Check for conventional commit format (keyword:)
                        if message.lower().startswith(f"{keyword.lower()}:") or \
                           message.lower().startswith(f"{keyword.lower()}("):
                            if category not in commits_by_category:
                                commits_by_category[category] = []
                            commits_by_category[category].append((commit_hash, message))
                            categorized = True
                            break
                        # Check for keyword in message
                        elif f" {keyword.lower()} " in f" {message.lower()} ":
                            if category not in commits_by_category:
                                commits_by_category[category] = []
                            commits_by_category[category].append((commit_hash, message))
                            categorized = True
                            break
                            
                    if categorized:
                        break
                        
                # If not categorized, add to "Other Changes"
                if not categorized:
                    if "Other Changes" not in commits_by_category:
                        commits_by_category["Other Changes"] = []
                    commits_by_category["Other Changes"].append((commit_hash, message))
        
        finally:
            # Restore original directory
            os.chdir(cwd)
    
    # Add categories and commits to release notes
    for category in sorted(commits_by_category.keys()):
        commits = commits_by_category[category]
        content += f"## {category}\n\n"
        
        for commit_hash, message in commits:
            # Check if message follows conventional commit format with scope
            scope_match = re.match(r'^(\w+)\(([^)]+)\):\s*(.+)$', message)
            if scope_match:
                type_name, scope, description = scope_match.groups()
                # Format with scope highlighted
                content += f"- **{scope}**: {description} ({commit_hash})\n"
            else:
                # Clean up conventional commit prefix if present
                cleaned_message = re.sub(r'^(\w+):\s*', '', message)
                content += f"- {cleaned_message} ({commit_hash})\n"
        
        content += "\n"
    
    # Add links to issues if issue tracker URL is provided
    if issue_tracker_url:
        # Extract issue numbers from commit messages
        issue_pattern = r'#(\d+)'
        all_issues = set()
        
        for category, commits in commits_by_category.items():
            for _, message in commits:
                for match in re.finditer(issue_pattern, message):
                    all_issues.add(match.group(1))
        
        if all_issues:
            content += "## Issues Addressed\n\n"
            for issue in sorted(all_issues, key=int):
                content += f"- [#{issue}]({issue_tracker_url}/{issue})\n"
            content += "\n"
    
    # Add contributors section
    if include_contributors and contributors:
        content += "## Contributors\n\n"
        for contributor in sorted(contributors):
            content += f"- {contributor}\n"
        content += "\n"
    
    # Create the MDP document
    doc = Document.create_with_auto_metadata(
        content=content,
        title=f"Release Notes - Version {version}",
        version=version,
        release_date=today,
        doc_type="release_notes"
    )
    
    # Save the document
    doc._mdp_file.path = Path(output_file)
    os.makedirs(doc._mdp_file.path.parent, exist_ok=True)
    doc.save()
    
    return doc


def generate_changelog(
    output_file: Union[str, Path],
    release_notes_dir: Union[str, Path],
    title: str = "Changelog",
    max_versions: Optional[int] = None,
    include_pattern: str = "*release*.mdp"
) -> Document:
    """
    Generate a changelog from release notes MDP documents.
    
    This function combines multiple release notes documents into a
    single changelog document.
    
    Args:
        output_file: Path to save the changelog document
        release_notes_dir: Directory containing release notes documents
        title: Title for the changelog document
        max_versions: Maximum number of versions to include (None for all)
        include_pattern: Pattern to match release notes files
        
    Returns:
        Document object for the generated changelog
    """
    notes_dir = Path(release_notes_dir)
    
    # Find release notes files
    release_files = list(notes_dir.glob(include_pattern))
    
    # Extract version info and sort by version (assuming semver)
    release_docs = []
    for path in release_files:
        try:
            doc = Document.from_file(path)
            # Extract version from metadata or content
            version = None
            if "version" in doc.metadata:
                version = doc.metadata["version"]
            else:
                # Try to extract from title
                title_match = re.search(r'Version\s+(\d+\.\d+\.\d+)', doc.content)
                if title_match:
                    version = title_match.group(1)
            
            if version:
                release_docs.append((version, doc))
        except Exception as e:
            print(f"Warning: Could not process {path}: {e}")
    
    # Sort by version (newest first)
    release_docs.sort(key=lambda x: [int(p) for p in x[0].split('.')], reverse=True)
    
    # Limit to max_versions if specified
    if max_versions:
        release_docs = release_docs[:max_versions]
    
    # Generate changelog content
    content = f"# {title}\n\n"
    content += "This document provides a summary of changes across releases.\n\n"
    
    for version, doc in release_docs:
        # Extract content from the release notes, skipping the title
        lines = doc.content.splitlines()
        if lines and lines[0].startswith("# "):
            # Skip the title line, but use it to create a section header
            content += f"## {lines[0][2:]}\n\n"
            content_start = 1
        else:
            content += f"## Version {version}\n\n"
            content_start = 0
            
        # Add the release content, skipping empty lines at the beginning
        while content_start < len(lines) and not lines[content_start].strip():
            content_start += 1
            
        release_content = "\n".join(lines[content_start:])
        content += release_content + "\n\n"
        content += "---\n\n"  # Separator between versions
    
    # Create the changelog document
    doc = Document.create_with_auto_metadata(
        content=content,
        title=title,
        doc_type="changelog"
    )
    
    # Save the document
    doc._mdp_file.path = Path(output_file)
    os.makedirs(doc._mdp_file.path.parent, exist_ok=True)
    doc.save()
    
    return doc 