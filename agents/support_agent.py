"""
Support Agent
Handles general customer support queries and ticket management
"""

from typing import Dict, Any, List
from datetime import datetime

class SupportAgent:
    """
    Specialist agent for customer support operations.
    Handles support queries, creates tickets, and provides solutions.
    """
    
    def __init__(self, mcp_server, name="SupportAgent"):
        self.name = name
        self.mcp_server = mcp_server
        self.capabilities = [
            "create_ticket",
            "handle_support_query",
            "escalate_issue",
            "provide_solution",
            "get_ticket_info"
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
            "help", "support", "issue", "problem", "ticket", 
            "upgrade", "cancel", "billing", "refund", "assistance",
            "question", "how to", "can't", "cannot", "error"
        ]
        return any(keyword in task_lower for keyword in keywords)
    
    def analyze_urgency(self, query: str) -> str:
        """
        Analyze query to determine priority level.
        
        Args:
            query: Customer query
            
        Returns:
            Priority level ('low', 'medium', 'high')
        """
        query_lower = query.lower()
        
        # High priority keywords
        high_priority = [
            "urgent", "immediately", "critical", "emergency", "asap",
            "charged twice", "cannot access", "locked out", "security",
            "fraud", "unauthorized", "hacked"
        ]
        
        # Medium priority keywords
        medium_priority = [
            "billing", "payment", "refund", "cancel", "upgrade",
            "not working", "broken", "error", "failed"
        ]
        
        if any(keyword in query_lower for keyword in high_priority):
            return "high"
        elif any(keyword in query_lower for keyword in medium_priority):
            return "medium"
        else:
            return "low"
    
    def detect_multiple_intents(self, query: str) -> List[str]:
        """
        Detect if query has multiple intents.
        
        Args:
            query: Customer query
            
        Returns:
            List of detected intents
        """
        intents = []
        query_lower = query.lower()
        
        intent_keywords = {
            "billing": ["billing", "charged", "payment", "invoice", "refund"],
            "cancellation": ["cancel", "unsubscribe", "stop subscription"],
            "upgrade": ["upgrade", "premium", "tier", "plan change"],
            "technical": ["not working", "error", "bug", "broken", "crash"],
            "account": ["account", "profile", "password", "login", "access"],
            "information": ["show", "get", "display", "what", "status"]
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                intents.append(intent)
        
        return intents
    
    def create_ticket(self, customer_id: int, issue: str, priority: str = None) -> Dict[str, Any]:
        """
        Create a support ticket.
        
        Args:
            customer_id: Customer ID
            issue: Issue description
            priority: Priority level (auto-detected if not provided)
            
        Returns:
            Ticket information
        """
        if priority is None:
            priority = self.analyze_urgency(issue)
        
        self.log(f"Creating {priority} priority ticket for customer {customer_id}")
        
        result = self.mcp_server.call_tool("create_ticket", {
            "customer_id": customer_id,
            "issue": issue,
            "priority": priority
        })
        
        if result["success"]:
            self.log(f"Created ticket: {result['result']['ticket_id']}")
            return result["result"]
        else:
            self.log(f"Failed to create ticket: {result['error']}", "ERROR")
            raise ValueError(result["error"])
    
    def needs_customer_context(self, query: str) -> bool:
        """
        Determine if query needs customer context.
        
        Args:
            query: Customer query
            
        Returns:
            True if customer context is needed
        """
        context_keywords = [
            "my account", "my subscription", "my billing", "my profile",
            "customer id", "i am", "i'm", "upgrade my", "cancel my"
        ]
        return any(keyword in query.lower() for keyword in context_keywords)
    
    def generate_solution(self, issue_type: str, customer_data: Dict[str, Any] = None) -> str:
        """
        Generate solution based on issue type.
        
        Args:
            issue_type: Type of issue
            customer_data: Optional customer context
            
        Returns:
            Solution text
        """
        solutions = {
            "billing": "I can help you with billing issues. Let me review your account and recent transactions.",
            "upgrade": "I'd be happy to help you upgrade your account. Let me check your current plan and available options.",
            "technical": "I understand you're experiencing technical difficulties. Let me investigate this issue for you.",
            "cancellation": "I'm sorry to hear you want to cancel. Let me help you with that process.",
            "account": "I can assist you with your account. Let me pull up your information.",
            "password": "For password issues, I can help you reset it securely."
        }
        
        return solutions.get(issue_type, "I'm here to help. Let me look into this for you.")
    
    def handle_support_query(self, query: str, customer_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle a customer support query.
        
        Args:
            query: Customer query
            customer_data: Optional customer information
            
        Returns:
            Response dictionary with solution and actions
        """
        self.log(f"Handling support query: {query[:50]}...")
        
        # Analyze the query
        priority = self.analyze_urgency(query)
        intents = self.detect_multiple_intents(query)
        needs_context = self.needs_customer_context(query)
        
        response = {
            "priority": priority,
            "intents": intents,
            "needs_customer_context": needs_context,
            "needs_escalation": len(intents) > 1 or priority == "high"
        }
        
        # Generate appropriate solution
        if intents:
            primary_intent = intents[0]
            response["solution"] = self.generate_solution(primary_intent, customer_data)
        else:
            response["solution"] = "I'm here to help. Could you provide more details about your issue?"
        
        # Add customer context if available
        if customer_data:
            response["customer_name"] = customer_data.get("name")
            response["customer_status"] = customer_data.get("status")
        
        self.log(f"Analysis complete - Priority: {priority}, Intents: {intents}")
        
        return response
    
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
            if action == "create_ticket":
                result = self.create_ticket(
                    params["customer_id"],
                    params["issue"],
                    params.get("priority")
                )
            elif action == "handle_query":
                result = self.handle_support_query(
                    params["query"],
                    params.get("customer_data")
                )
            elif action == "analyze_urgency":
                result = {"priority": self.analyze_urgency(params["query"])}
            elif action == "detect_intents":
                result = {"intents": self.detect_multiple_intents(params["query"])}
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