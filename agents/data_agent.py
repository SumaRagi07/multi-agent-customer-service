"""
Customer Data Agent
Specializes in accessing and managing customer data via MCP server
"""

from typing import Dict, Any, List
import json
from datetime import datetime

class CustomerDataAgent:
    """
    Specialist agent for customer data operations.
    Interfaces with MCP server to access customer database.
    """
    
    def __init__(self, mcp_server, name="CustomerDataAgent"):
        self.name = name
        self.mcp_server = mcp_server
        self.capabilities = [
            "get_customer_info",
            "list_customers",
            "update_customer_info",
            "get_customer_tickets",
            "validate_customer"
        ]
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{self.name}] [{level}] {message}")
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this agent can handle the given task.
        """
        task_lower = task.lower()
        keywords = [
            "customer", "account", "profile", "information", "data",
            "email", "phone", "status", "update", "get", "fetch", "retrieve"
        ]
        return any(keyword in task_lower for keyword in keywords)
    
    def get_customer_info(self, customer_id: int) -> Dict[str, Any]:
        """
        Get customer information by ID.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer data dictionary
        """
        self.log(f"Fetching customer info for ID: {customer_id}")
        
        result = self.mcp_server.call_tool("get_customer", {"customer_id": customer_id})
        
        if result["success"]:
            self.log(f"Successfully retrieved customer {customer_id}")
            return result["result"]
        else:
            self.log(f"Failed to get customer {customer_id}: {result['error']}", "ERROR")
            raise ValueError(result["error"])
    
    def list_customers(self, status: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List customers with optional status filter.
        
        Args:
            status: Filter by status ('active' or 'disabled')
            limit: Maximum number of customers
            
        Returns:
            List of customer dictionaries
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
            self.log(f"Listing {status} customers (limit: {limit})")
        else:
            self.log(f"Listing all customers (limit: {limit})")
        
        result = self.mcp_server.call_tool("list_customers", params)
        
        if result["success"]:
            self.log(f"Found {len(result['result'])} customers")
            return result["result"]
        else:
            self.log(f"Failed to list customers: {result['error']}", "ERROR")
            raise ValueError(result["error"])
    
    def update_customer_info(self, customer_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update customer information.
        
        Args:
            customer_id: Customer ID
            updates: Dictionary with fields to update
            
        Returns:
            Updated customer data
        """
        self.log(f"Updating customer {customer_id}: {updates}")
        
        result = self.mcp_server.call_tool("update_customer", {
            "customer_id": customer_id,
            "data": updates
        })
        
        if result["success"]:
            self.log(f"Successfully updated customer {customer_id}")
            return result["result"]
        else:
            self.log(f"Failed to update customer: {result['error']}", "ERROR")
            raise ValueError(result["error"])
    
    def get_customer_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """
        Get ticket history for a customer.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List of tickets
        """
        self.log(f"Fetching ticket history for customer {customer_id}")
        
        result = self.mcp_server.call_tool("get_customer_history", {
            "customer_id": customer_id
        })
        
        if result["success"]:
            tickets = result["result"]
            self.log(f"Found {len(tickets)} tickets for customer {customer_id}")
            return tickets
        else:
            self.log(f"Failed to get history: {result['error']}", "ERROR")
            raise ValueError(result["error"])
    
    def validate_customer_exists(self, customer_id: int) -> bool:
        """
        Check if customer exists.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            True if customer exists, False otherwise
        """
        try:
            self.get_customer_info(customer_id)
            return True
        except ValueError:
            return False
    
    def get_premium_customers(self) -> List[Dict[str, Any]]:
        """
        Get all active customers (treating active as premium for this demo).
        
        Returns:
            List of active customers
        """
        self.log("Fetching premium (active) customers")
        return self.list_customers(status="active", limit=100)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request from another agent.
        
        Args:
            request: Dictionary with 'action' and 'parameters'
            
        Returns:
            Response dictionary
        """
        action = request.get("action")
        params = request.get("parameters", {})
        
        self.log(f"Handling request: {action}")
        
        try:
            if action == "get_customer":
                result = self.get_customer_info(params["customer_id"])
            elif action == "list_customers":
                result = self.list_customers(
                    status=params.get("status"),
                    limit=params.get("limit", 10)
                )
            elif action == "update_customer":
                result = self.update_customer_info(
                    params["customer_id"],
                    params["updates"]
                )
            elif action == "get_history":
                result = self.get_customer_history(params["customer_id"])
            elif action == "validate_customer":
                result = {"exists": self.validate_customer_exists(params["customer_id"])}
            elif action == "get_premium_customers":
                result = self.get_premium_customers()
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return {
                "success": True,
                "agent": self.name,
                "result": result
            }
        except Exception as e:
            self.log(f"Error handling request: {str(e)}", "ERROR")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e)
            }