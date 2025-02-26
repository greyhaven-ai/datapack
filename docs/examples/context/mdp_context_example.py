#!/usr/bin/env python3
"""
Example script demonstrating the use of context in MDP files
to provide additional information for models.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datapack.mdp import MDPFile, write_mdp, read_mdp


def main():
    """Main function to demonstrate MDP context usage."""
    # Create metadata with context
    metadata = {
        "title": "Project Architecture Overview",
        "context": """
This document was created to help new developers understand the project structure.
It outlines the main components, their responsibilities, and how they interact.
The architecture follows a modular design with clear separation of concerns.

When analyzing code or answering questions about this project:
1. Use this document as a primary reference for understanding component relationships
2. Refer to specific modules mentioned when explaining code functionality
3. Consider the design principles outlined when suggesting improvements
4. Prioritize maintaining the existing architecture patterns
        """.strip(),
        
        # Other standard metadata
        "author": "Architecture Team",
        "tags": ["architecture", "overview", "documentation"],
        "created_at": "2023-05-15",
        "updated_at": "2023-05-16",
    }
    
    # Create content
    content = """# Project Architecture Overview

## Introduction

This document provides an overview of the project's architecture, explaining the main components
and how they interact with each other.

## Core Components

### Data Layer

The data layer is responsible for:
- Data storage and retrieval
- Data validation
- Data transformation

### Business Logic Layer

The business logic layer contains:
- Core domain models
- Business rules and validation
- Service orchestration

### Presentation Layer

The presentation layer handles:
- User interface components
- API endpoints
- Response formatting

## Component Interactions

Components interact through well-defined interfaces, following these principles:
1. Lower layers should not depend on higher layers
2. Communication between components should be explicit
3. Each component should have a single responsibility

## Design Decisions

Key architectural decisions include:
- Using a modular approach to enable independent development
- Implementing clear interfaces between components
- Prioritizing testability in the design
- Maintaining backward compatibility for public APIs
"""
    
    # Create the examples directory if it doesn't exist
    examples_dir = Path(__file__).parent
    output_path = examples_dir / "context_example.mdp"
    
    # Write the MDP file
    mdp_file = write_mdp(output_path, metadata, content)
    
    print(f"Created MDP file with context at: {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
    
    # Read back and display the context
    read_file = read_mdp(output_path)
    
    print("\nMetadata in the created file:")
    print(f"\nTitle: {read_file.metadata['title']}")
    
    print("\nContext:")
    print(f"{read_file.metadata['context']}")


if __name__ == "__main__":
    main() 