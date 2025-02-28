# Model Context Protocol (MCP) Module

This module provides integration between Datapack and the Model Context Protocol (MCP) ecosystem. It allows you to:

1. Run an MCP server that serves MDP documents
2. Connect to MCP servers to retrieve and manipulate documents
3. Fetch relevant context for AI models

## Overview

The MCP module includes two implementations:

1. **Official MCP SDK Integration** - Leverages the official [MCP Python SDK](https://github.com/model-context-protocol/mcp-python) for full compatibility with the MCP ecosystem
2. **Legacy Custom Implementation** - Original implementation (maintained for backward compatibility)

## Resource URI Structure

The MCP implementation uses the following URI structure for resources:

```
mdp://docs/{doc_id}                 # Document content
mdp://docs/{doc_id}/metadata        # Document metadata
mdp://collections/list               # List all documents
```

This aligns with the MDP URI format used in the core library: `mdp://organization/project/path`.

## Using the Official MCP SDK Integration

### Server-Side Usage

```python
from datapack.mcp.server_mcp import create_mcp_server

# Create and start an MCP server with a title
server = create_mcp_server("My Document Server") 
server.run()
```

The server provides the following capabilities:
- Document storage and retrieval
- Document search
- Context fetching
- Document metadata access

### Client-Side Usage

#### Asynchronous Client

```python
import asyncio
from mdp.document import Document
from datapack.mcp.client_mcp import DatapackMCPClient

async def main():
    # Create an async client
    # Pass the path to a server file or URL
    async with DatapackMCPClient("http://localhost:8000") as client:
        # Create a document
        doc = Document(
            content="This is a sample document.",
            metadata={"title": "Sample Document", "tags": ["example"]}
        )
        
        # Create a document
        result = await client.create_document(doc)
        doc_id = result.split(": ")[1]
        
        # Read a document
        doc = await client.read_document(doc_id)
        
        # Update a document
        doc.content += "\nAdditional content."
        result = await client.update_document(doc_id, doc)
        
        # Search documents
        results = await client.search_documents("sample")
        
        # Fetch context
        context = await client.fetch_context("sample document")
        
        # Delete a document
        result = await client.delete_document(doc_id)
        
        # List documents
        docs = await client.list_documents()

asyncio.run(main())
```

#### Synchronous Client

```python
from mdp.document import Document
from datapack.mcp.client_mcp import DatapackMCPClientSync

# Create a sync client
with DatapackMCPClientSync("http://localhost:8000") as client:
    # Create a document
    doc = Document(
        content="This is a sample document.",
        metadata={"title": "Sample Document", "tags": ["example"]}
    )
    
    # Create a document
    result = client.create_document(doc)
    doc_id = result.split(": ")[1]
    
    # Read a document
    doc = client.read_document(doc_id)
    
    # Update a document
    doc.content += "\nAdditional content."
    result = client.update_document(doc_id, doc)
    
    # Search documents
    results = client.search_documents("sample")
    
    # Fetch context
    context = client.fetch_context("sample document")
    
    # Delete a document
    result = client.delete_document(doc_id)
    
    # List documents
    docs = client.list_documents()
```

## Running the Example

The module includes a comprehensive example that demonstrates both server and client functionality:

```bash
# Run the server
python -m datapack.mcp.example_official_mcp --mode server

# In a separate terminal:
# Run the async client example
python -m datapack.mcp.example_official_mcp --mode async

# Or run the sync client example
python -m datapack.mcp.example_official_mcp --mode sync
```

## Legacy Implementation

For backward compatibility, the original custom implementation is still available:

```python
from datapack.mcp import MCPServer, MCPClient

# Start a server
server = MCPServer(port=8080)
server.start()

# Connect a client
client = MCPClient(host="localhost", port=8080)
# Use client methods...
``` 