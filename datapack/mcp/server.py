"""
MCP Server implementation for Datapack using the official MCP SDK.

This module provides server functionality for handling document operations
through the Model Context Protocol.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional, Any

from mcp.server.fastmcp import FastMCP, Context
import mcp.types as types

from datapack.mdp.document import Document
from datapack.mdp.collection import DocumentCollection, InMemoryCollection


class DatapackContext:
    """Context for the Datapack MCP server."""
    
    def __init__(self, collection: DocumentCollection):
        """
        Initialize the context.
        
        Args:
            collection: The document collection to use
        """
        self.collection = collection


@asynccontextmanager
async def datapack_lifespan(server: FastMCP) -> AsyncIterator[DatapackContext]:
    """
    Manage the lifecycle of the Datapack MCP server.
    
    Args:
        server: The MCP server instance
        
    Yields:
        The server context
    """
    # Create a collection - this could be replaced with a persistent collection
    # loaded from a database or file system
    collection = InMemoryCollection()
    
    # Initialize any resources here, like connecting to databases
    try:
        yield DatapackContext(collection=collection)
    finally:
        # Clean up resources on shutdown
        pass


def create_mcp_server(name: str = "Datapack") -> FastMCP:
    """
    Create and configure an MCP server for Datapack.
    
    Args:
        name: Name of the server
        
    Returns:
        The configured MCP server
    """
    # Create the MCP server
    mcp = FastMCP(name, lifespan=datapack_lifespan)
    
    # Define resources
    @mcp.resource("mdp://docs/{doc_id}")
    def get_document(doc_id: str, ctx: Context) -> str:
        """
        Get a document by ID.
        
        Args:
            doc_id: The document ID
            ctx: The MCP context
            
        Returns:
            The document content
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        doc = datapack_ctx.collection.get(doc_id)
        
        if not doc:
            raise ValueError(f"Document not found: {doc_id}")
        
        return doc.content
    
    @mcp.resource("mdp://docs/{doc_id}/metadata")
    def get_document_metadata(doc_id: str, ctx: Context) -> str:
        """
        Get document metadata by ID.
        
        Args:
            doc_id: The document ID
            ctx: The MCP context
            
        Returns:
            The document metadata as a string
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        doc = datapack_ctx.collection.get(doc_id)
        
        if not doc:
            raise ValueError(f"Document not found: {doc_id}")
        
        # Format metadata as a string
        metadata_str = "\n".join(f"{key}: {value}" for key, value in doc.metadata.items())
        return metadata_str
    
    @mcp.resource("mdp://collections/list")
    def list_documents(ctx: Context) -> str:
        """
        List all documents in the collection.
        
        Args:
            ctx: The MCP context
            
        Returns:
            A list of document IDs and titles
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        docs = datapack_ctx.collection.list()
        
        result = []
        for doc_id, doc in docs:
            title = doc.metadata.get("title", "Untitled")
            result.append(f"{doc_id}: {title}")
        
        return "\n".join(result)
    
    # Define tools
    @mcp.tool()
    def create_document(content: str, metadata: Optional[Dict[str, Any]] = None, ctx: Context) -> str:
        """
        Create a new document.
        
        Args:
            content: The document content
            metadata: Optional metadata
            ctx: The MCP context
            
        Returns:
            The ID of the created document
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        
        # Create the document
        doc = Document(content=content, metadata=metadata or {})
        
        # Add to collection
        doc_id = datapack_ctx.collection.add(doc)
        
        return f"Document created with ID: {doc_id}"
    
    @mcp.tool()
    def update_document(doc_id: str, content: Optional[str] = None, 
                       metadata: Optional[Dict[str, Any]] = None, ctx: Context) -> str:
        """
        Update an existing document.
        
        Args:
            doc_id: The document ID
            content: The updated content (optional)
            metadata: Updated metadata (optional)
            ctx: The MCP context
            
        Returns:
            A success message
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        
        # Check if the document exists
        if not datapack_ctx.collection.exists(doc_id):
            raise ValueError(f"Document not found: {doc_id}")
        
        # Get the current document
        doc = datapack_ctx.collection.get(doc_id)
        
        # Update content if provided
        if content is not None:
            doc.content = content
        
        # Update metadata if provided
        if metadata is not None:
            doc.metadata.update(metadata)
        
        # Save the updated document
        datapack_ctx.collection.update(doc_id, doc)
        
        return f"Document {doc_id} updated successfully"
    
    @mcp.tool()
    def delete_document(doc_id: str, ctx: Context) -> str:
        """
        Delete a document.
        
        Args:
            doc_id: The document ID
            ctx: The MCP context
            
        Returns:
            A success message
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        
        # Check if the document exists
        if not datapack_ctx.collection.exists(doc_id):
            raise ValueError(f"Document not found: {doc_id}")
        
        # Delete the document
        datapack_ctx.collection.remove(doc_id)
        
        return f"Document {doc_id} deleted successfully"
    
    @mcp.tool()
    def search_documents(query: str, max_results: int = 10, ctx: Context) -> str:
        """
        Search for documents.
        
        Args:
            query: The search query
            max_results: Maximum number of results (default: 10)
            ctx: The MCP context
            
        Returns:
            The search results
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        
        # Search the collection
        results = datapack_ctx.collection.search(query, max_results=max_results)
        
        # Format the results
        if not results:
            return "No matching documents found."
        
        formatted_results = []
        for doc_id, doc, score in results:
            title = doc.metadata.get("title", "Untitled")
            snippet = doc.get_snippet(query) if hasattr(doc, "get_snippet") else doc.content[:100] + "..."
            formatted_results.append(f"Document: {title} (ID: {doc_id}, Score: {score:.2f})\nSnippet: {snippet}\n")
        
        return "\n".join(formatted_results)
    
    @mcp.tool()
    def fetch_context(query: str, doc_ids: Optional[List[str]] = None, 
                     max_results: int = 5, ctx: Context) -> str:
        """
        Fetch context for a query from documents.
        
        Args:
            query: The query to fetch context for
            doc_ids: Optional list of document IDs to search within
            max_results: Maximum number of results (default: 5)
            ctx: The MCP context
            
        Returns:
            Contextual information from documents
        """
        datapack_ctx: DatapackContext = ctx.request_context.lifespan_context
        
        # If specific documents are requested, search only those
        if doc_ids:
            docs = []
            for doc_id in doc_ids:
                if datapack_ctx.collection.exists(doc_id):
                    docs.append((doc_id, datapack_ctx.collection.get(doc_id)))
        else:
            # Otherwise search all documents
            search_results = datapack_ctx.collection.search(query, max_results=max_results)
            docs = [(doc_id, doc) for doc_id, doc, _ in search_results]
        
        if not docs:
            return "No relevant documents found."
        
        # Extract context from each document
        contexts = []
        for doc_id, doc in docs:
            title = doc.metadata.get("title", "Untitled")
            # Use get_context if available, otherwise return relevant section
            if hasattr(doc, "get_context"):
                context = doc.get_context(query)
            else:
                # Simple context extraction - just get surrounding text
                query_pos = doc.content.lower().find(query.lower())
                if query_pos >= 0:
                    start = max(0, query_pos - 100)
                    end = min(len(doc.content), query_pos + len(query) + 100)
                    context = doc.content[start:end]
                else:
                    context = doc.content[:200]  # Just return beginning if query not found
            
            contexts.append(f"Document: {title} (ID: {doc_id})\nContext: {context}\n")
        
        return "\n".join(contexts)
    
    # Define prompts
    @mcp.prompt()
    def create_document_prompt() -> str:
        """Create a prompt for document creation."""
        return """
        I want to create a new document in the Datapack system.
        
        Please help me format this document with appropriate content and metadata.
        """
    
    @mcp.prompt()
    def search_documents_prompt() -> str:
        """Create a prompt for document search."""
        return """
        I need to search for specific information in my documents.
        
        Please help me construct an effective search query to find the most relevant documents.
        """
    
    return mcp


# Create a server instance when module is imported
datapack_mcp_server = create_mcp_server()

if __name__ == "__main__":
    # When run directly, start the server
    datapack_mcp_server.run() 