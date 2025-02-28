"""
Converters for transforming various data formats to MDP files.

This package provides tools for converting common data formats like JSON, XML, CSV,
YAML, Markdown, PDF, HTML, DOCX, Jupyter Notebooks, Email, SQL, and API responses
into MDP (Markdown Data Pack) files, preserving structure and metadata.
"""

from .json_converter import json_to_mdp
from .xml_converter import xml_to_mdp
from .csv_converter import csv_to_mdp
from .yaml_converter import yaml_to_mdp
from .markdown_converter import markdown_to_mdp
from .api_converter import api_response_to_mdp
from .sql_converter import sql_to_mdp, query_results_to_mdp

# Conditionally import converters that require additional dependencies
try:
    from .html_converter import html_to_mdp
    HTML_SUPPORT = True
except ImportError:
    HTML_SUPPORT = False

try:
    from .docx_converter import docx_to_mdp
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    from .notebook_converter import notebook_to_mdp
    NOTEBOOK_SUPPORT = True
except ImportError:
    NOTEBOOK_SUPPORT = False

try:
    from .email_converter import email_to_mdp
    EMAIL_SUPPORT = True
except ImportError:
    EMAIL_SUPPORT = False

try:
    from .pdf_converter import pdf_to_mdp
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

__all__ = [
    "json_to_mdp",
    "xml_to_mdp",
    "csv_to_mdp",
    "yaml_to_mdp",
    "markdown_to_mdp",
    "api_response_to_mdp",
    "sql_to_mdp",
    "query_results_to_mdp",
]

# Add conditionally imported converters if available
if HTML_SUPPORT:
    __all__.append("html_to_mdp")

if DOCX_SUPPORT:
    __all__.append("docx_to_mdp")

if NOTEBOOK_SUPPORT:
    __all__.append("notebook_to_mdp")

if EMAIL_SUPPORT:
    __all__.append("email_to_mdp")

if PDF_SUPPORT:
    __all__.append("pdf_to_mdp") 