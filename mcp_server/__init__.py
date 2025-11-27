"""
MCP Server for Customer Service System
Provides tools for customer data access and ticket management
"""

from .database import CustomerDatabase
from .server import MCPServer

__all__ = ['CustomerDatabase', 'MCPServer']