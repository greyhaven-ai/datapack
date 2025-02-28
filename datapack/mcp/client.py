"""
MCP Client implementation for Datapack using the official MCP SDK.

This module provides client functionality for interacting with MCP servers
to perform document operations.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.models import StdioServerParameters

from mdp.document import Document


class DatapackMCPClient:
    """
    Client for interacting with Datapack MCP servers.
    
    This class provides methods for performing document operations using
    the Model Context Protocol.
    """
    
    def __init__(
        self,
        server_path: str,
        server_args: Optional[List[str]] = None,
        server_env: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the MCP client.
        
        Args:
            server_path: Path to the MCP server script
            server_args: Optional arguments to pass to the server
            server_env: Optional environment variables for the server
        """
        self.server_parameters = StdioServerParameters(
            command="python",
            args=[server_path] + (server_args or []),
            env=server_env
        )
        self.session = None
    
    async def __aenter__(self):
        """
        Start the client session.
        
        Returns:
            The client instance
        """
        read_stream, write_stream = await stdio_client(self.server_parameters).__aenter__()
        self.session = await ClientSession(read_stream, write_stream).__aenter__()
        await self.session.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Close the client session.
        """
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
            self.session = None
    
    async def create_document(self, document: Document) -> str:
        """
        Create a new document.
        
        Args:
            document: The document to create
            
        Returns:
            Response from the server
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        result = await self.session.call_tool(
            "create_document",
            arguments={
                "content": document.content,
                "metadata": document.metadata
            }
        )
        
        return result
    
    async def read_document(self, document_id: str) -> Document:
        """
        Read a document by ID.
        
        Args:
            document_id: ID of the document to read
            
        Returns:
            The document
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        # Get document content
        content, _ = await self.session.read_resource(f"mdp://docs/{document_id}")
        
        # Get document metadata
        metadata_str, _ = await self.session.read_resource(f"mdp://docs/{document_id}/metadata")
        
        # Parse metadata from string
        metadata = {}
        for line in metadata_str.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split(":", 1)
            if len(parts) == 2:
                key, value = parts
                metadata[key.strip()] = value.strip()
        
        return Document(content=content, metadata=metadata)
    
    async def update_document(self, document_id: str, document: Document) -> str:
        """
        Update a document.
        
        Args:
            document_id: ID of the document to update
            document: The updated document
            
        Returns:
            Response from the server
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        result = await self.session.call_tool(
            "update_document",
            arguments={
                "doc_id": document_id,
                "content": document.content,
                "metadata": document.metadata
            }
        )
        
        return result
    
    async def delete_document(self, document_id: str) -> str:
        """
        Delete a document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            Response from the server
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        result = await self.session.call_tool(
            "delete_document",
            arguments={
                "doc_id": document_id
            }
        )
        
        return result
    
    async def search_documents(
        self,
        query: str,
        max_results: int = 10
    ) -> str:
        """
        Search for documents.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Search results
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        result = await self.session.call_tool(
            "search_documents",
            arguments={
                "query": query,
                "max_results": max_results
            }
        )
        
        return result
    
    async def fetch_context(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        max_results: int = 5
    ) -> str:
        """
        Fetch context for a query.
        
        Args:
            query: The query to fetch context for
            document_ids: Optional list of document IDs to search within
            max_results: Maximum number of results to return
            
        Returns:
            Context from relevant documents
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        args = {
            "query": query,
            "max_results": max_results
        }
        
        if document_ids:
            args["doc_ids"] = document_ids
        
        result = await self.session.call_tool(
            "fetch_context",
            arguments=args
        )
        
        return result
    
    async def list_documents(self) -> str:
        """
        List all documents.
        
        Returns:
            List of documents
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        content, _ = await self.session.read_resource("mdp://collections/list")
        return content


# Synchronous wrapper for easier usage
class DatapackMCPClientSync:
    """
    Synchronous wrapper around the async MCP client.
    
    This class provides a synchronous interface to the async client,
    making it easier to use in non-async code.
    """
    
    def __init__(
        self,
        server_path: str,
        server_args: Optional[List[str]] = None,
        server_env: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the sync client.
        
        Args:
            server_path: Path to the MCP server script
            server_args: Optional arguments to pass to the server
            server_env: Optional environment variables for the server
        """
        self.client = DatapackMCPClient(server_path, server_args, server_env)
        self._loop = None
    
    def _ensure_loop(self):
        """Ensure we have an event loop."""
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
    
    def __enter__(self):
        """Start the client session."""
        self._ensure_loop()
        self._enter_future = asyncio.run_coroutine_threadsafe(
            self.client.__aenter__(), self._loop
        )
        self._enter_future.result()  # Wait for completion
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the client session."""
        exit_future = asyncio.run_coroutine_threadsafe(
            self.client.__aexit__(exc_type, exc_val, exc_tb), self._loop
        )
        exit_future.result()  # Wait for completion
    
    def _run_async(self, coroutine):
        """Run an async function synchronously."""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        return future.result()
    
    def create_document(self, document: Document) -> str:
        """Create a new document."""
        return self._run_async(self.client.create_document(document))
    
    def read_document(self, document_id: str) -> Document:
        """Read a document by ID."""
        return self._run_async(self.client.read_document(document_id))
    
    def update_document(self, document_id: str, document: Document) -> str:
        """Update a document."""
        return self._run_async(self.client.update_document(document_id, document))
    
    def delete_document(self, document_id: str) -> str:
        """Delete a document."""
        return self._run_async(self.client.delete_document(document_id))
    
    def search_documents(self, query: str, max_results: int = 10) -> str:
        """Search for documents."""
        return self._run_async(self.client.search_documents(query, max_results))
    
    def fetch_context(self, query: str, document_ids: Optional[List[str]] = None, max_results: int = 5) -> str:
        """Fetch context for a query."""
        return self._run_async(self.client.fetch_context(query, document_ids, max_results))
    
    def list_documents(self) -> str:
        """List all documents."""
        return self._run_async(self.client.list_documents()) 