"""
Utility functions for converters.

This module provides utility functions used by the converters.
"""

from typing import Dict, Any, List, Set

# Standard MDP metadata fields
STANDARD_METADATA_FIELDS = {
    # Core fields
    "title",
    "version",
    "context",
    
    # Document identification fields
    "uuid",
    "uri",
    "local_path",
    "cid",
    
    # Collection fields
    "collection",
    "collection_id",
    "collection_id_type",
    "position",
    
    # Authorship fields
    "author",
    "contributors",
    "created_at",
    "updated_at",
    
    # Classification fields
    "tags",
    "status",
    
    # Source fields
    "source_file",
    "source_type",
    "source_url",
    
    # Relationship fields
    "relationships",
    
    # Source information (used by converters)
    "source",
}

def normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize metadata to conform to MDP standard fields.
    
    Non-standard fields are prefixed with 'x_' to mark them as custom fields.
    
    Args:
        metadata: The metadata dictionary to normalize
        
    Returns:
        A normalized metadata dictionary
    """
    normalized = {}
    
    # Process each metadata field
    for key, value in metadata.items():
        # If it's already a standard field or already has the custom prefix, keep as is
        if key in STANDARD_METADATA_FIELDS or key.startswith('x_'):
            normalized[key] = value
        else:
            # Otherwise, add the custom prefix
            normalized[f"x_{key}"] = value
    
    return normalized 