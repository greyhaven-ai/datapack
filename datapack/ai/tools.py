"""
AI tools for document processing.

This module provides tools that can be used by agents to process documents,
extract information, and perform specialized operations.
"""

from typing import List, Dict, Any, Optional, Union, Type, Callable
from pathlib import Path
import re
from datetime import datetime
import os

from pydantic_ai import RunContext
from pydantic import BaseModel, Field

from mdp import Document, Collection
from datapack.ai.dependencies import DocumentDependencies, CollectionDependencies, DocumentRepositoryDeps
from datapack.ai.models import Relationship, RelationshipType


class SimilaritySearchResult(BaseModel):
    """Result from a document similarity search."""
    title: str
    document_id: str
    path: Optional[str] = None
    similarity_score: float
    snippet: Optional[str] = None


class ExtractedReference(BaseModel):
    """A reference extracted from a document."""
    text: str
    context: str
    source_page: Optional[int] = None
    confidence: float


class KeyInsight(BaseModel):
    """A key insight extracted from a document."""
    topic: str
    insight: str
    confidence: float
    location: Optional[str] = None


async def search_for_documents(
    ctx: RunContext[DocumentRepositoryDeps],
    query: str,
    max_results: int = 5
) -> List[SimilaritySearchResult]:
    """
    Search for documents related to a query.
    
    This tool allows the agent to find documents in the repository
    that match a given search query.
    """
    results = []
    
    # Simple search implementation, this would be more sophisticated in production
    for doc_path, doc in ctx.deps.documents.items():
        # Calculate a basic similarity score based on word overlap
        query_words = set(query.lower().split())
        doc_words = set(doc.content.lower().split())
        if not query_words or not doc_words:
            continue
            
        overlap = len(query_words.intersection(doc_words))
        similarity = overlap / len(query_words) if query_words else 0
        
        if similarity > 0:
            # Get a snippet around the most relevant part
            snippet = None
            if overlap > 0:
                # Find a paragraph containing query terms
                paragraphs = doc.content.split("\n\n")
                for para in paragraphs:
                    if any(word in para.lower() for word in query_words):
                        snippet = para[:200] + "..." if len(para) > 200 else para
                        break
            
            results.append(SimilaritySearchResult(
                title=doc.title,
                document_id=doc.metadata.get("uuid", ""),
                path=str(doc.path) if doc.path else None,
                similarity_score=similarity,
                snippet=snippet
            ))
    
    # Sort by similarity and limit results
    results.sort(key=lambda x: x.similarity_score, reverse=True)
    return results[:max_results]


async def extract_references(
    ctx: RunContext[DocumentDependencies],
    reference_types: Optional[List[str]] = None
) -> List[ExtractedReference]:
    """
    Extract references from a document.
    
    This tool identifies and extracts citations, references, and links
    to other documents within the current document.
    """
    doc = ctx.deps.document
    
    # Default to all reference types if none specified
    if not reference_types:
        reference_types = ["citation", "link", "footnote"]
    
    references = []
    
    # Extract citations (e.g., [1], [Smith, 2020])
    if "citation" in reference_types:
        # Look for citation patterns
        citation_patterns = [
            r'\[([^\]]+)\]',  # [Author, Year] or [1]
            r'\(([^)]+\d{4}[^)]*)\)',  # (Author, Year)
        ]
        
        for pattern in citation_patterns:
            for match in re.finditer(pattern, doc.content):
                citation_text = match.group(1)
                start_pos = max(0, match.start() - 40)
                end_pos = min(len(doc.content), match.end() + 40)
                context = doc.content[start_pos:end_pos]
                
                references.append(ExtractedReference(
                    text=citation_text,
                    context=context,
                    confidence=0.8
                ))
    
    # Extract links (e.g., URLs, mdp:// links)
    if "link" in reference_types:
        # Look for URL patterns
        url_pattern = r'(https?://[^\s]+)'
        mdp_pattern = r'(mdp://[^\s]+)'
        
        for pattern in [url_pattern, mdp_pattern]:
            for match in re.finditer(pattern, doc.content):
                link_text = match.group(1)
                start_pos = max(0, match.start() - 40)
                end_pos = min(len(doc.content), match.end() + 40)
                context = doc.content[start_pos:end_pos]
                
                references.append(ExtractedReference(
                    text=link_text,
                    context=context,
                    confidence=0.9
                ))
    
    # Extract footnotes (e.g., [^1], [^note])
    if "footnote" in reference_types:
        footnote_pattern = r'\[\^([^\]]+)\]'
        
        for match in re.finditer(footnote_pattern, doc.content):
            footnote_id = match.group(1)
            
            # Try to find the footnote definition
            definition_pattern = r'\[\^' + re.escape(footnote_id) + r'\]:(.*?)(\n\[|\Z)'
            definition_match = re.search(definition_pattern, doc.content, re.DOTALL)
            
            context = ""
            if definition_match:
                context = definition_match.group(1).strip()
            
            references.append(ExtractedReference(
                text=f"[^{footnote_id}]",
                context=context,
                confidence=0.85
            ))
    
    return references


async def extract_key_insights(
    ctx: RunContext[DocumentDependencies],
    focus_areas: Optional[List[str]] = None,
    max_insights: int = 5
) -> List[KeyInsight]:
    """
    Extract key insights from a document.
    
    This tool identifies the most important points, findings, or
    insights from the document content.
    """
    doc = ctx.deps.document
    
    # Use a PydanticAI structured extractor to analyze the document
    # (In a real implementation, we would use the StructuredOutputGenerator here)
    
    # For demonstration, let's create some sample insights based on content analysis
    insights = []
    
    # Analyze headings (assume h1/h2 sections are important)
    heading_pattern = r'#{1,2}\s+([^\n]+)'
    headings = re.findall(heading_pattern, doc.content)
    
    for i, heading in enumerate(headings[:3]):
        # Get the content under this heading (simple approach)
        heading_pos = doc.content.find(heading)
        if heading_pos == -1:
            continue
            
        heading_pos += len(heading)
        next_heading_pos = doc.content.find('#', heading_pos)
        if next_heading_pos == -1:
            section_content = doc.content[heading_pos:]
        else:
            section_content = doc.content[heading_pos:next_heading_pos]
        
        # Create an insight based on the heading and content
        insights.append(KeyInsight(
            topic=heading,
            insight=f"The document covers {heading} with details on {section_content[:100]}...",
            confidence=0.8 - (i * 0.1),  # Decreasing confidence for later headings
            location=f"Section: {heading}"
        ))
    
    # Look for key statements (sentences with indicator phrases)
    key_indicators = [
        "importantly", "significantly", "in conclusion", "to summarize",
        "key point", "essential", "critical", "fundamental"
    ]
    
    sentences = re.split(r'(?<=[.!?])\s+', doc.content)
    for sentence in sentences:
        if any(indicator in sentence.lower() for indicator in key_indicators):
            insights.append(KeyInsight(
                topic="Key Statement",
                insight=sentence,
                confidence=0.85,
                location="Body text"
            ))
            
            if len(insights) >= max_insights:
                break
    
    # Filter insights by focus areas if specified
    if focus_areas:
        filtered_insights = []
        for insight in insights:
            if any(area.lower() in insight.topic.lower() or 
                   area.lower() in insight.insight.lower() 
                   for area in focus_areas):
                filtered_insights.append(insight)
        insights = filtered_insights
    
    # Sort by confidence and limit results
    insights.sort(key=lambda x: x.confidence, reverse=True)
    return insights[:max_insights]


async def create_document_relationship(
    ctx: RunContext[DocumentDependencies],
    target_document_id: str,
    relationship_type: str = "related",
    description: Optional[str] = None
) -> bool:
    """
    Create a relationship between the current document and another document.
    
    This tool establishes a connection between two documents, such as 
    parent/child relationships or references.
    """
    doc = ctx.deps.document
    
    # Validate relationship type
    if relationship_type not in ["parent", "child", "related", "reference"]:
        return False
    
    # Find the target document in related_documents
    target_doc = None
    for related_doc in ctx.deps.related_documents:
        if "uuid" in related_doc.metadata and related_doc.metadata["uuid"] == target_document_id:
            target_doc = related_doc
            break
    
    if not target_doc:
        return False
    
    # Add the relationship to the current document
    doc.add_relationship(
        target=target_doc,
        relationship_type=relationship_type,
        title=target_doc.title,
        description=description or f"{relationship_type.capitalize()} to {target_doc.title}"
    )
    
    # Add the reciprocal relationship to the target document
    if relationship_type == "parent":
        reciprocal_type = "child"
    elif relationship_type == "child":
        reciprocal_type = "parent"
    else:
        reciprocal_type = relationship_type
    
    target_doc.add_relationship(
        target=doc,
        relationship_type=reciprocal_type,
        title=doc.title,
        description=f"{reciprocal_type.capitalize()} to {doc.title}"
    )
    
    # Save both documents if they have paths
    if doc.path:
        doc.save()
    if target_doc.path:
        target_doc.save()
    
    return True


async def update_document_metadata(
    ctx: RunContext[DocumentDependencies],
    metadata_updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update metadata fields for the current document.
    
    This tool allows the agent to modify or add metadata to the document.
    """
    doc = ctx.deps.document
    
    # Track changes
    changes = {}
    
    for key, value in metadata_updates.items():
        # Handle special cases
        if key == "tags" and isinstance(value, list):
            # For tags, we append rather than replace
            current_tags = doc.metadata.get("tags", [])
            new_tags = [tag for tag in value if tag not in current_tags]
            if new_tags:
                doc.metadata["tags"] = current_tags + new_tags
                changes["tags"] = {
                    "action": "append",
                    "added": new_tags,
                    "result": doc.metadata["tags"]
                }
        elif key in ["created_at", "updated_at"] and isinstance(value, str):
            # For dates, validate format
            try:
                datetime.strptime(value, "%Y-%m-%d")
                old_value = doc.metadata.get(key)
                doc.metadata[key] = value
                changes[key] = {
                    "action": "update" if old_value else "add",
                    "old_value": old_value,
                    "new_value": value
                }
            except ValueError:
                # Invalid date format, skip
                pass
        else:
            # For other fields, simply update
            old_value = doc.metadata.get(key)
            doc.metadata[key] = value
            changes[key] = {
                "action": "update" if old_value else "add",
                "old_value": old_value,
                "new_value": value
            }
    
    # Update "updated_at" automatically if not already updated
    if "updated_at" not in changes:
        today = datetime.now().strftime("%Y-%m-%d")
        old_value = doc.metadata.get("updated_at")
        doc.metadata["updated_at"] = today
        changes["updated_at"] = {
            "action": "update" if old_value else "add",
            "old_value": old_value,
            "new_value": today
        }
    
    # Save the document if it has a path
    if doc.path:
        doc.save()
    
    return changes


async def extract_document_structure(
    ctx: RunContext[DocumentDependencies]
) -> Dict[str, Any]:
    """
    Extract the structure of the document.
    
    This tool analyzes the document and extracts its hierarchical structure,
    including headings, sections, and content organization.
    """
    doc = ctx.deps.document
    
    structure = {
        "title": doc.title,
        "sections": [],
        "headings": []
    }
    
    # Extract headings and their hierarchy
    heading_pattern = r'(#{1,6})\s+([^\n]+)'
    
    current_position = 0
    for match in re.finditer(heading_pattern, doc.content):
        level = len(match.group(1))
        heading_text = match.group(2).strip()
        
        # Get section content (from this heading to the next)
        start_pos = match.end()
        next_match = re.search(heading_pattern, doc.content[start_pos:])
        if next_match:
            end_pos = start_pos + next_match.start()
            section_content = doc.content[start_pos:end_pos].strip()
        else:
            section_content = doc.content[start_pos:].strip()
        
        structure["headings"].append({
            "text": heading_text,
            "level": level,
            "position": current_position
        })
        
        structure["sections"].append({
            "heading": heading_text,
            "level": level,
            "content": section_content,
            "position": current_position
        })
        
        current_position += 1
    
    # Extract any code blocks
    code_blocks = []
    code_pattern = r'```([a-z]*)\n(.*?)```'
    for match in re.finditer(code_pattern, doc.content, re.DOTALL):
        language = match.group(1) or "text"
        code = match.group(2)
        code_blocks.append({
            "language": language,
            "code": code
        })
    
    if code_blocks:
        structure["code_blocks"] = code_blocks
    
    # Extract any tables (simple markdown tables)
    tables = []
    table_pattern = r'(\|[^\n]+\|\n\|[-:| ]+\|\n(?:\|[^\n]+\|\n)+)'
    for match in re.finditer(table_pattern, doc.content):
        tables.append(match.group(1))
    
    if tables:
        structure["tables"] = tables
    
    return structure


async def find_document_dependencies(
    ctx: RunContext[DocumentDependencies]
) -> List[Dict[str, Any]]:
    """
    Find documents that this document depends on or that depend on it.
    
    This tool analyzes relationships and references to identify document dependencies.
    """
    doc = ctx.deps.document
    dependencies = []
    
    # Check explicit relationships in metadata
    if "relationships" in doc.metadata:
        for rel in doc.metadata["relationships"]:
            dependency = {
                "type": rel.get("type", "related"),
                "direction": "outgoing",
                "document_id": rel.get("id", ""),
                "title": rel.get("title", "Unknown document"),
                "description": rel.get("description", ""),
                "source": "explicit_relationship"
            }
            dependencies.append(dependency)
    
    # Check for documents that reference this document
    if ctx.deps.related_documents and "uuid" in doc.metadata:
        doc_uuid = doc.metadata["uuid"]
        for related_doc in ctx.deps.related_documents:
            if "relationships" in related_doc.metadata:
                for rel in related_doc.metadata["relationships"]:
                    if rel.get("id") == doc_uuid:
                        dependency = {
                            "type": rel.get("type", "related"),
                            "direction": "incoming",
                            "document_id": related_doc.metadata.get("uuid", ""),
                            "title": related_doc.title,
                            "description": rel.get("description", ""),
                            "source": "explicit_relationship"
                        }
                        dependencies.append(dependency)
    
    # Look for implicit references (mentions of this document's title in other documents)
    if ctx.deps.related_documents and doc.title:
        for related_doc in ctx.deps.related_documents:
            if doc.title in related_doc.content:
                # Only add if not already present as an explicit relationship
                is_duplicate = False
                for dep in dependencies:
                    if (dep["direction"] == "incoming" and
                        dep["document_id"] == related_doc.metadata.get("uuid", "")):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    dependency = {
                        "type": "reference",
                        "direction": "incoming",
                        "document_id": related_doc.metadata.get("uuid", ""),
                        "title": related_doc.title,
                        "description": f"Mentions {doc.title}",
                        "source": "implicit_reference"
                    }
                    dependencies.append(dependency)
    
    return dependencies


async def convert_file_to_mdp(
    ctx: RunContext[DocumentRepositoryDeps],
    file_path: str,
    output_filename: Optional[str] = None,
    extract_metadata: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Convert a file to MDP format.
    
    This tool converts various file formats (docx, pdf, html, etc.) to MDP format.
    """
    from pathlib import Path
    import importlib
    
    # Construct full file path
    full_path = ctx.deps.base_directory / file_path
    if not full_path.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    # Determine file type and get appropriate converter
    file_ext = full_path.suffix.lower()
    
    # Try to import the appropriate converter
    try:
        if file_ext == '.docx':
            from datapack.converters.docx_converter import docx_to_mdp
            converter_func = docx_to_mdp
        elif file_ext == '.pdf':
            from datapack.converters.pdf_converter import pdf_to_mdp
            converter_func = pdf_to_mdp
        elif file_ext == '.html' or file_ext == '.htm':
            from datapack.converters.html_converter import html_to_mdp
            converter_func = html_to_mdp
        elif file_ext == '.txt':
            from datapack.converters.text_converter import text_to_mdp
            converter_func = text_to_mdp
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_ext}"
            }
    except ImportError as e:
        return {
            "success": False,
            "error": f"Converter not available: {str(e)}"
        }
    
    # Determine output path
    if output_filename:
        output_path = ctx.deps.base_directory / output_filename
        if not output_path.suffix:
            output_path = output_path.with_suffix('.mdp')
    else:
        output_path = ctx.deps.base_directory / full_path.with_suffix('.mdp').name
    
    # Convert the file
    try:
        document = converter_func(full_path, output_path=output_path, extract_metadata=extract_metadata)
        
        # Add to the repository
        doc_key = str(output_path.relative_to(ctx.deps.base_directory))
        ctx.deps.documents[doc_key] = document
        
        return {
            "success": True,
            "document_path": str(output_path),
            "document_title": document.title,
            "extracted_metadata": dict(document.metadata)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Conversion failed: {str(e)}"
        }


async def update_document_content(
    ctx: RunContext[DocumentDependencies],
    new_content: str,
    section_identifier: Optional[str] = None,
    replace_entire_content: bool = False
) -> Dict[str, Any]:
    """
    Update the content of the current document.
    
    Args:
        ctx: The run context containing the document
        new_content: The new content to add or replace existing content
        section_identifier: If specified, replace only the identified section (e.g., "## Introduction")
        replace_entire_content: If True, replace the entire document content, otherwise append
        
    Returns:
        Dict with success status and information about the changes
    """
    doc = ctx.deps.document
    current_content = doc.content
    
    # Track changes
    result = {
        "success": True,
        "original_length": len(current_content),
    }
    
    if section_identifier and section_identifier in current_content:
        # Find the specified section and the start of the next section (if any)
        section_start = current_content.find(section_identifier)
        
        # Look for the next header at the same level or higher
        header_level = section_identifier.count('#')
        pattern = r'\n#{1,' + str(header_level) + r'}\s+[^\n]+'
        
        next_matches = list(re.finditer(pattern, current_content[section_start:]))
        if next_matches:
            section_end = section_start + next_matches[0].start()
            # Replace just this section (including its header)
            new_doc_content = (
                current_content[:section_start] + 
                section_identifier + '\n\n' + new_content + '\n\n' +
                current_content[section_end:]
            )
            result["action"] = "section_replaced"
            result["section"] = section_identifier
        else:
            # This is the last section, replace to the end
            new_doc_content = (
                current_content[:section_start] + 
                section_identifier + '\n\n' + new_content
            )
            result["action"] = "section_replaced"
            result["section"] = section_identifier
    elif replace_entire_content:
        # Replace the entire content
        new_doc_content = new_content
        result["action"] = "content_replaced"
    else:
        # Append to the existing content
        new_doc_content = current_content + "\n\n" + new_content
        result["action"] = "content_appended"
    
    # Update the document with the new content
    doc.content = new_doc_content
    
    # Save the document if it has a path
    if doc.path:
        doc.save()
        result["saved_to"] = str(doc.path)
    
    result["new_length"] = len(doc.content)
    result["difference"] = result["new_length"] - result["original_length"]
    
    return result


async def add_context_to_document(
    ctx: RunContext[DocumentDependencies],
    context: str,
    position: str = "end",  # "start", "end", or section identifier
    format_as_comment: bool = False
) -> Dict[str, Any]:
    """
    Add contextual information to a document without modifying the main content.
    
    Args:
        ctx: The run context containing the document
        context: The contextual information to add
        position: Where to add the context - "start", "end", or a section identifier
        format_as_comment: If True, format the context as a Markdown comment <!-- -->
        
    Returns:
        Dict with success status and information about the changes
    """
    doc = ctx.deps.document
    current_content = doc.content
    
    # Format the context if needed
    if format_as_comment:
        formatted_context = f"<!-- {context} -->\n\n"
    else:
        formatted_context = f"{context}\n\n"
    
    result = {
        "success": True,
        "original_length": len(current_content),
        "context_length": len(formatted_context)
    }
    
    if position == "start":
        # Add at the start
        new_doc_content = formatted_context + current_content
        result["action"] = "context_added_to_start"
    elif position == "end":
        # Add at the end
        new_doc_content = current_content + "\n\n" + formatted_context
        result["action"] = "context_added_to_end"
    elif position in current_content:
        # Find the specified section
        section_pos = current_content.find(position)
        if section_pos >= 0:
            # Find the end of the section header line
            line_end = current_content.find('\n', section_pos)
            if line_end >= 0:
                # Insert after the section header
                new_doc_content = (
                    current_content[:line_end + 1] + 
                    "\n" + formatted_context +
                    current_content[line_end + 1:]
                )
                result["action"] = "context_added_to_section"
                result["section"] = position
            else:
                # If no line end found, append to the end
                new_doc_content = current_content + "\n\n" + formatted_context
                result["action"] = "context_added_to_end"
        else:
            # If section not found, append to the end
            new_doc_content = current_content + "\n\n" + formatted_context
            result["action"] = "context_added_to_end"
    else:
        # Default to adding at the end
        new_doc_content = current_content + "\n\n" + formatted_context
        result["action"] = "context_added_to_end"
    
    # Update the document with the new content
    doc.content = new_doc_content
    
    # Save the document if it has a path
    if doc.path:
        doc.save()
        result["saved_to"] = str(doc.path)
    
    result["new_length"] = len(doc.content)
    result["difference"] = result["new_length"] - result["original_length"]
    
    return result


async def query_document(
    ctx: RunContext[DocumentDependencies],
    query: str,
    section: Optional[str] = None,
    max_context_length: int = 1000
) -> Dict[str, Any]:
    """
    Query the document for specific information and return relevant context.
    
    Args:
        ctx: The run context containing the document
        query: The question or search query
        section: Optional section to limit the search to
        max_context_length: Maximum length of context to return
        
    Returns:
        Dict with query results, including relevant context
    """
    doc = ctx.deps.document
    content = doc.content
    
    # If section specified, extract only that section
    if section and section in content:
        section_start = content.find(section)
        
        # Find the next section header
        header_level = section.count('#')
        pattern = r'\n#{1,' + str(header_level) + r'}\s+[^\n]+'
        
        next_matches = list(re.finditer(pattern, content[section_start:]))
        if next_matches:
            section_end = section_start + next_matches[0].start()
            search_content = content[section_start:section_end]
        else:
            # This is the last section
            search_content = content[section_start:]
    else:
        search_content = content
    
    # Process query to find most relevant context
    # This is a simple implementation - in a real system, use embeddings or better search
    relevance_score = 0
    
    # Look for exact matches or similar terms
    query_terms = query.lower().split()
    content_lower = search_content.lower()
    
    # Check for direct matches of the query
    direct_match = query.lower() in content_lower
    if direct_match:
        relevance_score = 0.9
        
        # Find the match position and extract surrounding context
        match_pos = content_lower.find(query.lower())
        
        # Get surrounding context
        start_pos = max(0, match_pos - max_context_length // 2)
        end_pos = min(len(search_content), match_pos + len(query) + max_context_length // 2)
        
        # Try to extend to paragraph boundaries
        while start_pos > 0 and search_content[start_pos] != '\n':
            start_pos -= 1
            
        while end_pos < len(search_content) and search_content[end_pos] != '\n':
            end_pos += 1
            
        # Extract the context
        context = search_content[start_pos:end_pos].strip()
        
    else:
        # Count term matches as a fallback
        term_matches = sum(1 for term in query_terms if term in content_lower)
        if term_matches > 0:
            relevance_score = min(0.7, term_matches / len(query_terms))
            
            # Extract a relevant section based on term density
            paragraphs = search_content.split('\n\n')
            scored_paragraphs = []
            
            for para in paragraphs:
                para_lower = para.lower()
                score = sum(1 for term in query_terms if term in para_lower) / len(para)
                scored_paragraphs.append((score, para))
                
            # Get best paragraph
            scored_paragraphs.sort(reverse=True)
            if scored_paragraphs:
                context = scored_paragraphs[0][1]
                if len(context) > max_context_length:
                    context = context[:max_context_length] + "..."
            else:
                context = ""
        else:
            # No relevant content found
            relevance_score = 0
            context = "No relevant content found for this query."
    
    return {
        "success": True,
        "query": query,
        "relevance_score": relevance_score,
        "context": context,
        "document_title": doc.title,
        "document_id": doc.id
    }


async def modify_collection(
    ctx: RunContext[CollectionDependencies],
    action: str,  # "add" or "remove"
    document_paths: List[str],
    update_relationships: bool = True
) -> Dict[str, Any]:
    """
    Add or remove documents from a collection.
    
    Args:
        ctx: The run context containing the collection
        action: "add" or "remove"
        document_paths: List of paths to documents to add or remove
        update_relationships: Whether to update relationships between documents
        
    Returns:
        Dict with success status and information about the changes
    """
    collection = ctx.deps.collection
    
    result = {
        "success": True,
        "action": action,
        "initial_document_count": len(collection.documents),
        "processed_paths": document_paths,
        "processed_count": 0,
        "failed_paths": []
    }
    
    if action == "add":
        for path_str in document_paths:
            path = Path(path_str)
            try:
                if not path.exists():
                    result["failed_paths"].append({"path": path_str, "reason": "File not found"})
                    continue
                    
                if path.suffix != ".mdp":
                    result["failed_paths"].append({"path": path_str, "reason": "Not an MDP file"})
                    continue
                
                # Load the document
                document = Document.from_file(path)
                
                # Add to collection
                collection.add_document(document)
                result["processed_count"] += 1
                
            except Exception as e:
                result["failed_paths"].append({"path": path_str, "reason": str(e)})
    
    elif action == "remove":
        for path_str in document_paths:
            try:
                # Try to find document by path
                doc_to_remove = None
                for doc in collection.documents:
                    if doc.path and str(doc.path) == path_str:
                        doc_to_remove = doc
                        break
                
                if doc_to_remove:
                    collection.remove_document(doc_to_remove.id)
                    result["processed_count"] += 1
                else:
                    result["failed_paths"].append({"path": path_str, "reason": "Document not found in collection"})
            
            except Exception as e:
                result["failed_paths"].append({"path": path_str, "reason": str(e)})
    
    else:
        result["success"] = False
        result["error"] = f"Invalid action: {action}. Must be 'add' or 'remove'."
        return result
    
    # Save the collection
    if collection.path:
        collection.save()
        result["saved_to"] = str(collection.path)
    
    result["final_document_count"] = len(collection.documents)
    result["difference"] = result["final_document_count"] - result["initial_document_count"]
    
    return result 