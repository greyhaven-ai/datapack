# Datapack Workflows

This directory contains workflow utilities for managing and processing documents in various contexts.

## Overview

The workflows package provides higher-level functionality that builds on top of the core MDP file format and utilities. These workflows are organized by domain rather than being tightly coupled to the MDP format itself.

## Directory Structure

- `__init__.py` - Package exports and documentation
- `dev.py` - Development-focused workflows for code documentation and API generation
- `releases.py` - Release management workflows for version documentation
- `content.py` - Content manipulation workflows for batch processing and merging documents

## Usage

### Development Workflows

```python
from datapack.workflows.dev import generate_api_docs

# Generate API documentation for a Python module
api_doc = generate_api_docs(
    code_directory="./my_package",
    output_file="./docs/api_reference.mdp",
    module_name="my_package"
)
```

### Release Workflows

```python
from datapack.workflows.releases import create_release_notes

# Generate release notes from git commits
notes = create_release_notes(
    version="1.0.0",
    output_file="./docs/releases/v1.0.0.mdp",
    source_directory=".",
    git_log_range="v0.9.0..HEAD"
)
```

### Content Workflows

```python
from datapack.workflows.content import merge_documents
from datapack.mdp import Document

# Merge multiple documents into one
doc1 = Document.from_file("./docs/part1.mdp")
doc2 = Document.from_file("./docs/part2.mdp")

merged = merge_documents(
    docs=[doc1, doc2],
    output_path="./docs/complete.mdp",
    title="Complete Documentation"
)
```

## Command Line Use

The workflows in this package are also accessible through the `mdp` command-line interface:

```bash
# Generate API documentation
mdp dev api-docs ./my_package ./docs/api_reference.mdp --module-name my_package

# Create release notes
mdp release notes 1.0.0 ./docs/releases/v1.0.0.mdp --source-dir . --git-range v0.9.0..HEAD

# Merge documents
mdp content merge ./docs/part1.mdp ./docs/part2.mdp --output ./docs/complete.mdp --title "Complete Documentation"
``` 