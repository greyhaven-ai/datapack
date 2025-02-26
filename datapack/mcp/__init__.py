"""
MCP (Model Context Protocol) module for Datapack.

This module provides server and client implementations for interacting with
document processing using the Model Context Protocol.
"""

# Legacy MCP implementation (backward compatibility)
from datapack.mcp.client import MCPClient
from datapack.mcp.server import MCPServer
from datapack.mcp.protocol import MCPRequestHandler, MCPRequest, MCPResponse

# New MCP implementation using the official MCP SDK
from datapack.mcp.server import create_mcp_server, datapack_mcp_server
from datapack.mcp.client import DatapackMCPClient, DatapackMCPClientSync

__all__ = [
    # Legacy MCP implementation
    "MCPClient",
    "MCPServer",
    "MCPRequestHandler",
    "MCPRequest", 
    "MCPResponse",
    
    # New MCP implementation
    "create_mcp_server",
    "datapack_mcp_server",
    "DatapackMCPClient",
    "DatapackMCPClientSync",
] 