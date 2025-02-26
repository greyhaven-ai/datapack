"""
MDP (Markdown Document Protocol) module for the datapack package.

This module provides tools for working with MDP documents, collections,
and related formatting.
"""

from datapack.mdp.document import Document
from datapack.mdp.collection import Collection
from datapack.mdp.converter import convert_to_html, convert_to_pdf

# Define what gets imported with "from datapack.mdp import *"
__all__ = [
    'Document',
    'Collection',
    'convert_to_html',
    'convert_to_pdf',
] 