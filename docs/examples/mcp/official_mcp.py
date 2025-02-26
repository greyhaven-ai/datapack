"""
Example script demonstrating how to use the official MCP implementation.

This script shows how to:
1. Start an MCP server
2. Connect to it with the client
3. Perform document operations

The MCP implementation uses the standard MDP URI format:
- mdp://docs/{doc_id} - Access document content
- mdp://docs/{doc_id}/metadata - Access document metadata
- mdp://collections/list - List all documents
"""

import os
import asyncio
import argparse
from pathlib import Path

from datapack.mdp.document import Document
from datapack.mcp.server import create_mcp_server
from datapack.mcp.client import DatapackMCPClient, DatapackMCPClientSync


async def run_async_example():
    """Run an example using the async client."""
    # Get the path to this file
    server_file = Path(__file__).resolve()
    
    print("Starting async client example...")
    
    # Create an async client
    async with DatapackMCPClient(str(server_file)) as client:
        # Create some documents
        doc1 = Document(
            content="This is a sample document about artificial intelligence. "
                    "AI systems are designed to perform tasks that typically require human intelligence.",
            metadata={"title": "Introduction to AI", "tags": ["AI", "technology"]}
        )
        
        doc2 = Document(
            content="Python is a high-level programming language known for its simplicity and readability. "
                    "It's widely used in data science, machine learning, and web development.",
            metadata={"title": "Python Programming", "tags": ["programming", "Python"]}
        )
        
        # Create documents
        print("Creating documents...")
        result1 = await client.create_document(doc1)
        result2 = await client.create_document(doc2)
        print(f"Document 1: {result1}")
        print(f"Document 2: {result2}")
        
        # Extract document IDs from the creation results
        # The format should be "Document created with ID: <id>"
        doc1_id = result1.split(": ")[1]
        doc2_id = result2.split(": ")[1]
        
        # List documents
        print("\nListing documents (uses mdp://collections/list):")
        docs = await client.list_documents()
        print(docs)
        
        # Read a document
        print(f"\nReading document {doc1_id} (uses mdp://docs/{doc1_id}):")
        retrieved_doc = await client.read_document(doc1_id)
        print(f"Title: {retrieved_doc.metadata.get('title')}")
        print(f"Content: {retrieved_doc.content[:50]}...")
        
        # Update a document
        print(f"\nUpdating document {doc1_id}:")
        doc1.content += "\n\nThis is additional information about AI."
        doc1.metadata["updated"] = True
        update_result = await client.update_document(doc1_id, doc1)
        print(update_result)
        
        # Search for documents
        print("\nSearching for documents about 'Python':")
        search_results = await client.search_documents("Python")
        print(search_results)
        
        # Fetch context
        print("\nFetching context for 'programming':")
        context = await client.fetch_context("programming")
        print(context)
        
        # Delete a document
        print(f"\nDeleting document {doc2_id}:")
        delete_result = await client.delete_document(doc2_id)
        print(delete_result)
        
        # List documents again
        print("\nListing documents after deletion:")
        docs = await client.list_documents()
        print(docs)


def run_sync_example():
    """Run an example using the synchronous client."""
    # Get the path to this file
    server_file = Path(__file__).resolve()
    
    print("Starting synchronous client example...")
    
    # Create a sync client
    with DatapackMCPClientSync(str(server_file)) as client:
        # Create some documents
        doc1 = Document(
            content="This is a sample document about machine learning. "
                    "ML is a subset of AI focused on enabling systems to learn from data.",
            metadata={"title": "Introduction to ML", "tags": ["ML", "AI"]}
        )
        
        doc2 = Document(
            content="JavaScript is a programming language commonly used for web development. "
                    "It allows for interactive web pages and is an essential part of web applications.",
            metadata={"title": "JavaScript Basics", "tags": ["programming", "JavaScript"]}
        )
        
        # Create documents
        print("Creating documents...")
        result1 = client.create_document(doc1)
        result2 = client.create_document(doc2)
        print(f"Document 1: {result1}")
        print(f"Document 2: {result2}")
        
        # Extract document IDs from the creation results
        doc1_id = result1.split(": ")[1]
        doc2_id = result2.split(": ")[1]
        
        # List documents
        print("\nListing documents (uses mdp://collections/list):")
        docs = client.list_documents()
        print(docs)
        
        # Read a document
        print(f"\nReading document {doc1_id} (uses mdp://docs/{doc1_id}):")
        retrieved_doc = client.read_document(doc1_id)
        print(f"Title: {retrieved_doc.metadata.get('title')}")
        print(f"Content: {retrieved_doc.content[:50]}...")
        
        # Search for documents
        print("\nSearching for documents about 'programming':")
        search_results = client.search_documents("programming")
        print(search_results)
        
        # Delete documents
        print(f"\nDeleting documents:")
        delete_result1 = client.delete_document(doc1_id)
        delete_result2 = client.delete_document(doc2_id)
        print(delete_result1)
        print(delete_result2)


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(description="Run MCP examples")
    parser.add_argument(
        "--mode",
        choices=["async", "sync", "server"],
        default="server",
        help="Run in async client, sync client, or server mode"
    )
    
    args = parser.parse_args()
    
    if args.mode == "async":
        asyncio.run(run_async_example())
    elif args.mode == "sync":
        run_sync_example()
    else:
        # Start the server
        print("Starting MCP server...")
        print("The server exposes resources using the MDP URI format:")
        print("- mdp://docs/{doc_id}")
        print("- mdp://docs/{doc_id}/metadata")
        print("- mdp://collections/list")
        server = create_mcp_server("Datapack Example")
        server.run()


if __name__ == "__main__":
    main() 