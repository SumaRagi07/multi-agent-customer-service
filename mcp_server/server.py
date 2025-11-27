"""
MCP Server Implementation
Provides 5 tools for customer service operations via MCP protocol
"""

from typing import Any, Dict, List
import json
from .database import CustomerDatabase

class MCPServer:
    """
    MCP Server that exposes customer service tools.
    Implements the 5 required tools from the assignment.
    """
    
    def __init__(self, db_path="support.db"):
        self.db = CustomerDatabase(db_path)
        self.tools = {
            "get_customer": self.get_customer,
            "list_customers": self.list_customers,
            "update_customer": self.update_customer,
            "create_ticket": self.create_ticket,
            "get_customer_history": self.get_customer_history,
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Return list of available tools with their schemas.
        """
        return [
            {
                "name": "get_customer",
                "description": "Get customer information by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "The customer ID"
                        }
                    },
                    "required": ["customer_id"]
                }
            },
            {
                "name": "list_customers",
                "description": "List customers with optional status filter",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["active", "disabled"],
                            "description": "Filter by customer status (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        }
                    }
                }
            },
            {
                "name": "update_customer",
                "description": "Update customer information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "The customer ID"
                        },
                        "data": {
                            "type": "object",
                            "description": "Fields to update (name, email, phone, status)",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["active", "disabled"]
                                }
                            }
                        }
                    },
                    "required": ["customer_id", "data"]
                }
            },
            {
                "name": "create_ticket",
                "description": "Create a new support ticket",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "The customer ID"
                        },
                        "issue": {
                            "type": "string",
                            "description": "Description of the issue"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Priority level (default: medium)",
                            "default": "medium"
                        }
                    },
                    "required": ["customer_id", "issue"]
                }
            },
            {
                "name": "get_customer_history",
                "description": "Get all tickets for a customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "The customer ID"
                        }
                    },
                    "required": ["customer_id"]
                }
            }
        ]
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Dictionary with result or error
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            result = self.tools[tool_name](**parameters)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Tool implementations
    
    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get customer by ID"""
        customer = self.db.get_customer(customer_id)
        if customer:
            return customer
        else:
            raise ValueError(f"Customer {customer_id} not found")
    
    def list_customers(self, status: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List customers with optional filter"""
        return self.db.list_customers(status, limit)
    
    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information"""
        success = self.db.update_customer(customer_id, data)
        if success:
            # Return updated customer
            return self.db.get_customer(customer_id)
        else:
            raise ValueError(f"Failed to update customer {customer_id}")
    
    def create_ticket(self, customer_id: int, issue: str, priority: str = "medium") -> Dict[str, Any]:
        """Create a new ticket"""
        ticket_id = self.db.create_ticket(customer_id, issue, priority)
        if ticket_id:
            return {
                "ticket_id": ticket_id,
                "customer_id": customer_id,
                "issue": issue,
                "priority": priority,
                "status": "open"
            }
        else:
            raise ValueError(f"Failed to create ticket for customer {customer_id}")
    
    def get_customer_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get customer's ticket history"""
        tickets = self.db.get_customer_history(customer_id)
        return tickets