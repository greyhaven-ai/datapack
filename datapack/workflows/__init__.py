"""
Workflow modules for MDP document management.

This package provides domain-specific workflows for managing MDP documents.
It includes modules for development workflows, documentation workflows, 
release management, and content extraction.
"""

# Import domain-specific workflows
from datapack.workflows.dev import (
    sync_codebase_docs,
    extract_docs_from_source,
    generate_api_docs,
)

from datapack.workflows.releases import (
    create_release_notes,
    generate_changelog,
)

from datapack.workflows.content import (
    batch_process_documents,
    extract_document_sections,
    create_document_from_template,
    merge_documents,
)

# Define __all__ to control imports with "from datapack.workflows import *"
__all__ = [
    # Development workflows
    "sync_codebase_docs",
    "extract_docs_from_source",
    "generate_api_docs",
    
    # Release workflows
    "create_release_notes",
    "generate_changelog",
    
    # Content workflows
    "batch_process_documents",
    "extract_document_sections",
    "create_document_from_template",
    "merge_documents",
] 