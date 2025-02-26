"""
Datapack: A document ingestion, parsing, and annotation platform.

This package provides tools for working with various document types,
adding metadata, and sharing across software ecosystems.
"""

# Direct imports for convenience
from datapack.mdp import Document, Collection
import datapack.workflows

# Try to import AI capabilities but don't fail if not available
try:
    import datapack.ai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Define version
__version__ = "0.1.0"

# CLI entry point
def cli():
    """Command-line interface entry point."""
    from datapack.cli import main
    main()

# Check if AI capabilities are available
def has_ai_capabilities():
    """Check if AI capabilities are available."""
    return AI_AVAILABLE

# What to import with "from datapack import *"
__all__ = [
    "Document",
    "Collection",
    "workflows",
    "has_ai_capabilities",
]

# Add AI to __all__ if available
if AI_AVAILABLE:
    __all__.append("ai")
