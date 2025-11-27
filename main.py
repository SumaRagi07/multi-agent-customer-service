"""
Main Execution Script
Multi-Agent Customer Service System with A2A and MCP
"""

import sys
from mcp_server.database_setup import setup_database
from mcp_server import MCPServer
from agents import RouterAgent, CustomerDataAgent, SupportAgent

def initialize_system():
    """
    Initialize the entire system:
    1. Setup database
    2. Initialize MCP server
    3. Initialize agents
    """
    print("=" * 80)
    print("Initializing Multi-agent Customer Service System")
    print("=" * 80)
    print()
    
    # Step 1: Setup database
    print("Step 1: Setting up database...")
    db_path = setup_database()
    print()
    
    # Step 2: Initialize MCP Server
    print("Step 2: Initializing MCP Server...")
    mcp_server = MCPServer(db_path)
    print(f"✓ MCP Server initialized with {len(mcp_server.get_available_tools())} tools")
    print()
    
    # Step 3: Initialize Agents
    print("Step 3: Initializing Agents...")
    data_agent = CustomerDataAgent(mcp_server)
    print(f"✓ {data_agent.name} initialized")
    
    support_agent = SupportAgent(mcp_server)
    print(f"✓ {support_agent.name} initialized")
    
    router_agent = RouterAgent(data_agent, support_agent)
    print(f"✓ {router_agent.name} initialized")
    print()
    
    print("=" * 80)
    print("SYSTEM READY")
    print("=" * 80)
    print()
    
    return router_agent

def run_test_scenario(router_agent, scenario_num, query):
    """
    Run a single test scenario.
    
    Args:
        router_agent: The router agent
        scenario_num: Scenario number
        query: Customer query
    """
    print("\n")
    print("=" * 80)
    print(f"TEST SCENARIO {scenario_num}")
    print("=" * 80)
    print(f"Query: {query}")
    print("-" * 80)
    print()
    
    # Clear previous coordination log
    router_agent.clear_coordination_log()
    
    # Process query
    response = router_agent.process_query(query)
    
    print()
    print("-" * 80)
    print("FINAL RESPONSE:")
    print("-" * 80)
    print(response)
    print()
    print("=" * 80)
    print()

def run_automated_tests(router_agent):
    """Run the 5 required test scenarios"""
    # Test Scenarios from Assignment
    test_scenarios = [
        # Scenario 1: Simple Query - Single agent, straightforward MCP call
        ("Get customer information for ID 5", 1),
        
        # Scenario 2: Coordinated Query - Multiple agents coordinate
        ("I'm customer 2 and need help upgrading my account", 2),
        
        # Scenario 3: Complex Query - Requires negotiation between agents
        ("Show me all active customers who have open tickets", 3),
        
        # Scenario 4: Escalation - Router must identify urgency
        ("I've been charged twice, please refund immediately!", 4),
        
        # Scenario 5: Multi-Intent - Parallel task execution
        ("Update my email to newemail@test.com and show my ticket history for customer 1", 5),
    ]
    
    print("\n")
    print("=" * 80)
    print("RUNNING 5 REQUIRED TEST SCENARIOS")
    print("=" * 80)
    
    for query, scenario_num in test_scenarios:
        run_test_scenario(router_agent, scenario_num, query)
        if scenario_num < 5:
            input("Press Enter to continue to next scenario...")
    
    print("\n")
    print("=" * 80)
    print("ALL TEST SCENARIOS COMPLETED")
    print("=" * 80)
    print()

def run_interactive_mode(router_agent):
    """Run interactive query mode"""
    print("\n")
    print("=" * 80)
    print("INTERACTIVE MODE")
    print("=" * 80)
    print("\nEnter your queries below. Type 'exit' to quit.")
    print("-" * 80)
    
    while True:
        print("\nYour query: ", end="")
        query = input().strip()
        
        if query.lower() == 'exit':
            print("\nExiting interactive mode.")
            break
        
        if query:
            print()
            router_agent.clear_coordination_log()
            response = router_agent.process_query(query)
            print("\n" + "-" * 80)
            print("RESPONSE:")
            print("-" * 80)
            print(response)
            print("-" * 80)

def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 80)
    print("MULTI-AGENT CUSTOMER SERVICE SYSTEM - MAIN MENU")
    print("=" * 80)
    print("\nWhat would you like to do?\n")
    print("  1. Run the 5 Required Test Scenarios from Assignment (Automated)")
    print("  2. Enter Interactive Mode (Custom Queries)")
    print("  3. Run Both (Tests + Interactive)")
    print("  4. Exit")
    print("\n" + "-" * 80)

def main():
    """Main execution function"""
    
    # Initialize system
    router_agent = initialize_system()
    
    # Display menu
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            # Run automated tests only
            run_automated_tests(router_agent)
            print("\nReturning to main menu...")
            
        elif choice == '2':
            # Run interactive mode only
            run_interactive_mode(router_agent)
            print("\nReturning to main menu...")
            
        elif choice == '3':
            # Run both
            run_automated_tests(router_agent)
            print("\nAutomated tests complete! Now entering interactive mode...\n")
            input("Press Enter to continue...")
            run_interactive_mode(router_agent)
            print("\nReturning to main menu...")
            
        elif choice == '4':
            # Exit
            print("\n" + "=" * 80)
            print("Thank you for using the Multi-Agent Customer Service System!")
            print("=" * 80 + "\n")
            break
            
        else:
            print("\n⚠️  Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()