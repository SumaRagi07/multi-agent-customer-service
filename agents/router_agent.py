"""
Router Agent (Orchestrator)
Coordinates between specialist agents using A2A communication
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
import re

class RouterAgent:
    """
    Orchestrator agent that routes queries to specialist agents.
    Implements Agent-to-Agent (A2A) coordination.
    """
    
    def __init__(self, data_agent, support_agent, name="RouterAgent"):
        self.name = name
        self.data_agent = data_agent
        self.support_agent = support_agent
        self.conversation_history = []
        self.coordination_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{self.name}] [{level}] {message}"
        print(log_entry)
        self.coordination_log.append(log_entry)
    
    def log_a2a_communication(self, from_agent: str, to_agent: str, message: str):
        """Log agent-to-agent communication"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [A2A] {from_agent} → {to_agent}: {message}"
        print(log_entry)
        self.coordination_log.append(log_entry)
    
    def extract_customer_id(self, query: str) -> int:
        """
        Extract customer ID from query.
        
        Args:
            query: Customer query
            
        Returns:
            Customer ID or None
        """
        # Look for patterns like "customer ID 12345", "customer 12345", "ID: 12345"
        patterns = [
            r'customer\s+id\s*:?\s*(\d+)',
            r'id\s*:?\s*(\d+)',
            r'customer\s+(\d+)',
            r'\bI\'m\s+customer\s+(\d+)',
        ]
        
        query_lower = query.lower()
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return int(match.group(1))
        
        return None
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze customer query to determine routing strategy.
        
        Args:
            query: Customer query
            
        Returns:
            Analysis dictionary with intent and routing info
        """
        self.log(f"Analyzing query: {query[:80]}...")
        
        query_lower = query.lower()
        analysis = {
            "query": query,
            "customer_id": self.extract_customer_id(query),
            "needs_data_agent": False,
            "needs_support_agent": False,
            "needs_coordination": False,
            "complexity": "simple",
            "intents": []
        }
        
        # Determine which agents are needed
        if self.data_agent.can_handle(query):
            analysis["needs_data_agent"] = True
            analysis["intents"].append("data")
        
        if self.support_agent.can_handle(query):
            analysis["needs_support_agent"] = True
            analysis["intents"].append("support")
        
        # Determine complexity
        # Check for specific patterns first, then general patterns
        if "active customers" in query_lower and "tickets" in query_lower:
            # Special case: multi-step query for customers with tickets
            analysis["complexity"] = "multi-step"
            analysis["needs_coordination"] = True
        elif len(analysis["intents"]) > 1:
            analysis["complexity"] = "complex"
            analysis["needs_coordination"] = True
        elif any(keyword in query_lower for keyword in ["all", "list", "show me", "get all"]):
            analysis["complexity"] = "complex"
            analysis["needs_coordination"] = True
        
        # Detect multi-step queries
        if any(keyword in query_lower for keyword in ["and", "also", "then", "after"]):
            analysis["complexity"] = "multi-step"
            analysis["needs_coordination"] = True
        # Also detect standalone update operations as multi-step
        elif ("update" in query_lower or "change" in query_lower) and ("email" in query_lower or "phone" in query_lower):
            analysis["complexity"] = "multi-step"
            analysis["needs_coordination"] = True
        # Detect analytical ticket queries (e.g., "status of all high-priority tickets")
        elif ("status" in query_lower or "what is" in query_lower) and "ticket" in query_lower and "priority" in query_lower:
            analysis["complexity"] = "multi-step"
            analysis["needs_coordination"] = True
            if "data" not in analysis["intents"]:
                analysis["intents"].append("data")
            if "support" not in analysis["intents"]:
                analysis["intents"].append("support")
        
        self.log(f"Analysis: {analysis['complexity']} query, needs: {analysis['intents']}")
        
        return analysis
    
    def route_to_data_agent(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to Data Agent.
        
        Args:
            action: Action to perform
            parameters: Action parameters
            
        Returns:
            Response from Data Agent
        """
        self.log_a2a_communication(self.name, self.data_agent.name, f"{action} with params: {parameters}")
        
        request = {
            "action": action,
            "parameters": parameters,
            "from_agent": self.name
        }
        
        response = self.data_agent.handle_request(request)
        
        self.log_a2a_communication(
            self.data_agent.name,
            self.name,
            f"Response: {'Success' if response['success'] else 'Failed'}"
        )
        
        return response
    
    def route_to_support_agent(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to Support Agent.
        
        Args:
            action: Action to perform
            parameters: Action parameters
            
        Returns:
            Response from Support Agent
        """
        self.log_a2a_communication(self.name, self.support_agent.name, f"{action} with params: {parameters}")
        
        request = {
            "action": action,
            "parameters": parameters,
            "from_agent": self.name
        }
        
        response = self.support_agent.handle_request(request)
        
        self.log_a2a_communication(
            self.support_agent.name,
            self.name,
            f"Response: {'Success' if response['success'] else 'Failed'}"
        )
        
        return response
    
    def negotiate_between_agents(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate between multiple agents for complex queries.
        
        Args:
            query: Customer query
            analysis: Query analysis
            
        Returns:
            Coordinated response
        """
        self.log("Starting agent negotiation for complex query")
        
        coordinated_response = {
            "query": query,
            "responses": {},
            "final_answer": ""
        }
        
        # Check if Support Agent can handle it alone
        if analysis["needs_support_agent"]:
            self.log_a2a_communication(self.name, self.support_agent.name, "Can you handle this query?")
            
            support_response = self.route_to_support_agent("handle_query", {
                "query": query
            })
            
            coordinated_response["responses"]["support"] = support_response
            
            # If support agent needs customer context
            if support_response["success"] and support_response["result"].get("needs_customer_context"):
                self.log("Support Agent needs customer context, requesting from Data Agent")
                
                if analysis["customer_id"]:
                    data_response = self.route_to_data_agent("get_customer", {
                        "customer_id": analysis["customer_id"]
                    })
                    
                    coordinated_response["responses"]["data"] = data_response
                    
                    # Re-query Support Agent with context
                    if data_response["success"]:
                        self.log("Providing customer context to Support Agent")
                        support_response_with_context = self.route_to_support_agent("handle_query", {
                            "query": query,
                            "customer_data": data_response["result"]
                        })
                        coordinated_response["responses"]["support_with_context"] = support_response_with_context
        
        return coordinated_response
    
    def handle_simple_query(self, query: str, analysis: Dict[str, Any]) -> str:
        """
        Handle simple, single-agent queries.
        
        Args:
            query: Customer query
            analysis: Query analysis
            
        Returns:
            Response string
        """
        self.log("Handling simple query")
        
        query_lower = query.lower()
        
        # Handle "what is the name/email/phone/status of customer X" queries
        if analysis["customer_id"] and any(word in query_lower for word in ["what is", "what's"]):
            if any(field in query_lower for field in ["name", "email", "phone", "status", "information", "info"]):
                customer_id = analysis["customer_id"]
                response = self.route_to_data_agent("get_customer", {"customer_id": customer_id})
                if response["success"]:
                    customer = response["result"]
                    # Extract the specific field if asked
                    if "name" in query_lower and "email" not in query_lower:
                        return f"The name of customer {customer_id} is {customer['name']}."
                    elif "email" in query_lower:
                        return f"The email of customer {customer_id} is {customer['email']}."
                    elif "phone" in query_lower:
                        return f"The phone of customer {customer_id} is {customer['phone']}."
                    elif "status" in query_lower:
                        return f"Customer {customer_id} status is {customer['status']}."
                    else:
                        # Return full info
                        return f"Customer Information:\n" \
                               f"Name: {customer['name']}\n" \
                               f"Email: {customer['email']}\n" \
                               f"Phone: {customer['phone']}\n" \
                               f"Status: {customer['status']}"
                else:
                    return f"Error: {response['error']}"
        
        # Handle customer info queries
        if any(phrase in query_lower for phrase in ["get customer", "show me customer", "customer information"]):
            customer_id = analysis["customer_id"]
            if customer_id:
                response = self.route_to_data_agent("get_customer", {"customer_id": customer_id})
                if response["success"]:
                    customer = response["result"]
                    return f"Customer Information:\n" \
                           f"Name: {customer['name']}\n" \
                           f"Email: {customer['email']}\n" \
                           f"Phone: {customer['phone']}\n" \
                           f"Status: {customer['status']}"
                else:
                    return f"Error: {response['error']}"
        
        # Handle history queries
        if ("history" in query_lower or "tickets" in query_lower) and analysis["customer_id"]:
            history_response = self.route_to_data_agent("get_history", {
                "customer_id": analysis["customer_id"]
            })
            
            if history_response["success"]:
                tickets = history_response["result"]
                if tickets:
                    result = f"Ticket History for Customer {analysis['customer_id']}:\n"
                    for ticket in tickets:
                        result += f"  • [{ticket['status'].upper()}] {ticket['issue']}\n"
                        result += f"    Priority: {ticket['priority']}, Created: {ticket['created_at']}\n"
                    return result.strip()
                else:
                    return f"No tickets found for customer {analysis['customer_id']}"
            else:
                return f"Error: {history_response['error']}"
        
        # Default to support agent
        response = self.route_to_support_agent("handle_query", {"query": query})
        if response["success"]:
            return response["result"].get("solution", "I'm here to help!")
        else:
            return f"Error: {response['error']}"
    
    def handle_complex_query(self, query: str, analysis: Dict[str, Any]) -> str:
        """
        Handle complex queries requiring coordination.
        
        Args:
            query: Customer query
            analysis: Query analysis
            
        Returns:
            Response string
        """
        self.log("Handling complex query with agent coordination")
        
        query_lower = query.lower()
        
        # Special case: show/get ticket history queries (prioritize this check)
        if ("ticket" in query_lower or "history" in query_lower) and analysis["customer_id"]:
            # Check if it's specifically asking for tickets, not just mentioning "show"
            if "ticket" in query_lower or "history" in query_lower:
                customer_id = analysis["customer_id"]
                
                # Get ticket history
                history_response = self.route_to_data_agent("get_history", {
                    "customer_id": customer_id
                })
                
                if history_response["success"]:
                    tickets = history_response["result"]
                    if tickets:
                        result = f"Ticket History for Customer {customer_id}:\n"
                        for ticket in tickets:
                            result += f"  • [{ticket['status'].upper()}] {ticket['issue']}\n"
                            result += f"    Priority: {ticket['priority']}, Created: {ticket['created_at']}\n"
                        return result.strip()
                    else:
                        return f"No tickets found for customer {customer_id}"
                else:
                    return f"Error: {history_response['error']}"
        
        # Special case: list customers
        elif "list" in query_lower and "customer" in query_lower:
            # Extract status if mentioned
            status = None
            if "active" in query_lower:
                status = "active"
            elif "disabled" in query_lower:
                status = "disabled"
            
            list_response = self.route_to_data_agent("list_customers", {
                "status": status,
                "limit": 10
            })
            
            if list_response["success"]:
                customers = list_response["result"]
                if customers:
                    result = f"Customer List ({len(customers)} customers):\n"
                    for customer in customers:
                        result += f"  • {customer['name']} (ID: {customer['id']}, Status: {customer['status']})\n"
                    return result.strip()
                else:
                    return "No customers found"
            else:
                return f"Error: {list_response['error']}"
        
        # Special case: show me customer X
        elif "show" in query_lower and "customer" in query_lower and analysis["customer_id"]:
            customer_id = analysis["customer_id"]
            response = self.route_to_data_agent("get_customer", {"customer_id": customer_id})
            
            if response["success"]:
                customer = response["result"]
                return f"Customer Information:\n" \
                       f"Name: {customer['name']}\n" \
                       f"Email: {customer['email']}\n" \
                       f"Phone: {customer['phone']}\n" \
                       f"Status: {customer['status']}"
            else:
                return f"Error: {response['error']}"
        
        # Default complex query handling with negotiation
        else:
            coordinated = self.negotiate_between_agents(query, analysis)
        
        # Synthesize final response
        parts = []
        
        if "data" in coordinated["responses"] and coordinated["responses"]["data"]["success"]:
            customer = coordinated["responses"]["data"]["result"]
            parts.append(f"Customer: {customer['name']} ({customer['status']})")
        
        if "support_with_context" in coordinated["responses"]:
            support_result = coordinated["responses"]["support_with_context"]["result"]
            parts.append(support_result.get("solution", ""))
        elif "support" in coordinated["responses"]:
            support_result = coordinated["responses"]["support"]["result"]
            parts.append(support_result.get("solution", ""))
        
        return "\n".join(parts) if parts else "I'm working on your request."
    
    def handle_multi_step_query(self, query: str, analysis: Dict[str, Any]) -> str:
        """
        Handle multi-step queries requiring sequential coordination.
        
        Args:
            query: Customer query
            analysis: Query analysis
            
        Returns:
            Response string
        """
        self.log("Handling multi-step query")
        
        results = []
        query_lower = query.lower()
        
        # Case 0: Analytical queries about tickets (e.g., "status of all high-priority tickets")
        if ("what is" in query_lower or "status" in query_lower) and "ticket" in query_lower and "priority" in query_lower:
            self.log("Analytical ticket query detected")
            
            # Check if asking about specific priority
            priority_filter = None
            if "high" in query_lower and "priority" in query_lower:
                priority_filter = "high"
            elif "medium" in query_lower and "priority" in query_lower:
                priority_filter = "medium"
            elif "low" in query_lower and "priority" in query_lower:
                priority_filter = "low"
            
            # Get active/premium customers
            customers_response = self.route_to_data_agent("get_premium_customers", {})
            
            if customers_response["success"]:
                customers = customers_response["result"]
                
                # Collect ticket statistics
                filtered_tickets = []
                
                for customer in customers[:10]:  # Limit to first 10 for performance
                    history_response = self.route_to_data_agent("get_history", {
                        "customer_id": customer["id"]
                    })
                    
                    if history_response["success"]:
                        tickets = history_response["result"]
                        for ticket in tickets:
                            if priority_filter is None or ticket["priority"] == priority_filter:
                                filtered_tickets.append({
                                    "customer": customer["name"],
                                    "issue": ticket["issue"],
                                    "status": ticket["status"],
                                    "priority": ticket["priority"]
                                })
                
                if filtered_tickets:
                    priority_desc = f"{priority_filter}-priority " if priority_filter else ""
                    results.append(f"Found {len(filtered_tickets)} {priority_desc}tickets:\n")
                    for ticket in filtered_tickets[:10]:  # Show first 10
                        results.append(f"  • {ticket['customer']}: [{ticket['status'].upper()}] {ticket['issue']}")
                        results.append(f"    Priority: {ticket['priority']}")
                else:
                    priority_desc = f"{priority_filter}-priority " if priority_filter else ""
                    results.append(f"No {priority_desc}tickets found.")
            else:
                results.append("Unable to retrieve ticket data.")
        
        # Case 1: "Show me all active customers who have open tickets"
        elif "active customers" in query_lower and "tickets" in query_lower:
            # Step 1: Get premium/active customers
            self.log("Step 1: Getting active customers")
            customers_response = self.route_to_data_agent("get_premium_customers", {})
            
            if customers_response["success"]:
                customers = customers_response["result"]
                results.append(f"Found {len(customers)} active customers")
                
                # Step 2: Get tickets for each customer
                self.log("Step 2: Getting tickets for customers")
                customers_with_tickets = []
                
                for customer in customers[:5]:  # Limit for demo
                    history_response = self.route_to_data_agent("get_history", {
                        "customer_id": customer["id"]
                    })
                    
                    if history_response["success"]:
                        tickets = history_response["result"]
                        open_tickets = [t for t in tickets if t["status"] == "open"]
                        if open_tickets:
                            customers_with_tickets.append({
                                "customer": customer,
                                "open_tickets": len(open_tickets)
                            })
                
                # Step 3: Format results
                if customers_with_tickets:
                    results.append(f"\nActive customers with open tickets:")
                    for item in customers_with_tickets:
                        results.append(
                            f"- {item['customer']['name']}: {item['open_tickets']} open ticket(s)"
                        )
                else:
                    results.append("No active customers with open tickets found.")
        
        # Case 2: Update email and show history (check this BEFORE simple history)
        elif "update" in query_lower and "email" in query_lower and analysis["customer_id"]:
            customer_id = analysis["customer_id"]
            
            # Extract email (simple pattern)
            import re
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
            if email_match:
                new_email = email_match.group(0)
                
                self.log(f"Step 1: Updating email for customer {customer_id}")
                # Update email
                update_response = self.route_to_data_agent("update_customer", {
                    "customer_id": customer_id,
                    "updates": {"email": new_email}
                })
                
                if update_response["success"]:
                    results.append(f"✓ Email updated to {new_email} for customer {customer_id}")
                else:
                    results.append(f"Error updating email: {update_response.get('error', 'Unknown error')}")
                
                # Show history if requested
                if "history" in query_lower or "ticket" in query_lower:
                    self.log(f"Step 2: Getting ticket history for customer {customer_id}")
                    history_response = self.route_to_data_agent("get_history", {
                        "customer_id": customer_id
                    })
                    
                    if history_response["success"]:
                        tickets = history_response["result"]
                        results.append(f"\nTicket History:")
                        for ticket in tickets:
                            results.append(f"  - [{ticket['status'].upper()}] {ticket['issue']} (Priority: {ticket['priority']})")
                    else:
                        results.append(f"No tickets found")
            else:
                results.append("Could not extract email address from query")
        
        # Case 2b: Update phone (without history)
        elif "update" in query_lower and "phone" in query_lower and analysis["customer_id"]:
            customer_id = analysis["customer_id"]
            
            # Extract phone number (simple pattern for XXX-XXXX format)
            import re
            phone_match = re.search(r'\d{3}-?\d{4}', query)
            if phone_match:
                new_phone = phone_match.group(0)
                
                self.log(f"Updating phone for customer {customer_id}")
                update_response = self.route_to_data_agent("update_customer", {
                    "customer_id": customer_id,
                    "updates": {"phone": new_phone}
                })
                
                if update_response["success"]:
                    results.append(f"✓ Phone updated to {new_phone} for customer {customer_id}")
                    # Show updated customer info
                    customer = update_response["result"]
                    results.append(f"\nUpdated Customer Information:")
                    results.append(f"  Name: {customer['name']}")
                    results.append(f"  Email: {customer['email']}")
                    results.append(f"  Phone: {customer['phone']}")
                else:
                    results.append(f"Error updating phone: {update_response.get('error', 'Unknown error')}")
            else:
                results.append("Could not extract phone number from query")
        
        # Case 2c: Change/update email (different wording)
        elif ("change" in query_lower or "update" in query_lower) and "email" in query_lower and analysis["customer_id"]:
            customer_id = analysis["customer_id"]
            
            # Extract email
            import re
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
            if email_match:
                new_email = email_match.group(0)
                
                self.log(f"Changing email for customer {customer_id}")
                update_response = self.route_to_data_agent("update_customer", {
                    "customer_id": customer_id,
                    "updates": {"email": new_email}
                })
                
                if update_response["success"]:
                    results.append(f"✓ Email changed to {new_email} for customer {customer_id}")
                    customer = update_response["result"]
                    results.append(f"\nUpdated Customer Information:")
                    results.append(f"  Name: {customer['name']}")
                    results.append(f"  Email: {customer['email']}")
                else:
                    results.append(f"Error changing email: {update_response.get('error', 'Unknown error')}")
            else:
                results.append("Could not extract email address from query")
        
        # Case 3: "ticket history" or "show tickets" for a customer
        elif ("ticket" in query_lower or "history" in query_lower) and analysis["customer_id"]:
            customer_id = analysis["customer_id"]
            self.log(f"Getting ticket history for customer {customer_id}")
            
            history_response = self.route_to_data_agent("get_history", {
                "customer_id": customer_id
            })
            
            if history_response["success"]:
                tickets = history_response["result"]
                if tickets:
                    results.append(f"Ticket History for Customer {customer_id}:")
                    for ticket in tickets:
                        results.append(
                            f"  - [{ticket['status'].upper()}] {ticket['issue']} "
                            f"(Priority: {ticket['priority']}, ID: {ticket['id']})"
                        )
                else:
                    results.append(f"No tickets found for customer {customer_id}")
            else:
                results.append(f"Error: {history_response['error']}")
        
        # Case 4: Customer needs help (with customer ID) - expanded patterns
        elif analysis["customer_id"] and (
            "help" in query_lower or 
            "need" in query_lower or 
            "having" in query_lower or
            "here" in query_lower or
            "issue" in query_lower or
            "problem" in query_lower
        ):
            customer_id = analysis["customer_id"]
            
            # Step 1: Get customer data
            data_response = self.route_to_data_agent("get_customer", {
                "customer_id": customer_id
            })
            
            if data_response["success"]:
                customer = data_response["result"]
                
                # Step 2: Get support response with context
                support_response = self.route_to_support_agent("handle_query", {
                    "query": query,
                    "customer_data": customer
                })
                
                if support_response["success"]:
                    results.append(f"Hello {customer['name']}!")
                    results.append(support_response["result"]["solution"])
                else:
                    results.append("I'm here to help. Please provide more details.")
            else:
                results.append(f"Error: {data_response['error']}")
        
        return "\n".join(results) if results else "Query processed."
    
    def process_query(self, query: str) -> str:
        """
        Main entry point for processing customer queries.
        
        Args:
            query: Customer query
            
        Returns:
            Final response string
        """
        self.log(f"=" * 80)
        self.log(f"NEW QUERY: {query}")
        self.log(f"=" * 80)
        
        # Analyze query
        analysis = self.analyze_query(query)
        
        # Route based on complexity
        if analysis["complexity"] == "simple":
            response = self.handle_simple_query(query, analysis)
        elif analysis["complexity"] == "multi-step":
            response = self.handle_multi_step_query(query, analysis)
        else:
            response = self.handle_complex_query(query, analysis)
        
        self.log(f"Query processing complete")
        self.log(f"=" * 80)
        
        return response
    
    def get_coordination_log(self) -> List[str]:
        """Get the full coordination log"""
        return self.coordination_log
    
    def clear_coordination_log(self):
        """Clear the coordination log"""
        self.coordination_log = []