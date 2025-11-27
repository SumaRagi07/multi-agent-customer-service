# Multi-Agent Customer Service System

A multi-agent system demonstrating Agent-to-Agent (A2A) communication and Model Context Protocol (MCP) integration for customer service automation.

## System Architecture

Three specialized agents coordinate to handle customer queries:
- **Router Agent** (Orchestrator): Analyzes queries and routes to appropriate agents
- **Customer Data Agent** (Specialist): Handles database operations via MCP tools
- **Support Agent** (Specialist): Provides customer support with priority detection

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone [https://github.com/SumaRagi07/multi-agent-customer-service]
cd multi-agent-customer-service
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Run the system
```bash
python main.py
```

### Menu Options
1. **Run 5 Required Test Scenarios** - Automated testing of assignment requirements
2. **Interactive Mode** - Enter custom queries
3. **Run Both** - Tests followed by interactive mode
4. **Exit**

## Test Scenarios

The system handles 5 required scenarios:

1. **Simple Query**: `"Get customer information for ID 5"`
   - Single agent data retrieval

2. **Coordinated Query**: `"I'm customer 2 and need help upgrading my account"`
   - Multiple agents coordinate with customer context

3. **Complex Multi-Step**: `"Show me all active customers who have open tickets"`
   - Sequential agent coordination and data filtering

4. **Escalation**: `"I've been charged twice, please refund immediately!"`
   - Priority detection and urgent routing

5. **Multi-Intent**: `"Update my email to newemail@test.com and show my ticket history for customer 1"`
   - Parallel task execution across agents

## MCP Tools

The MCP server provides 5 database tools:
- `get_customer(customer_id)` - Retrieve customer information
- `list_customers(status, limit)` - List customers with filters
- `update_customer(customer_id, data)` - Update customer records
- `create_ticket(customer_id, issue, priority)` - Create support tickets
- `get_customer_history(customer_id)` - Get customer ticket history

## Database Schema

**Customers Table**: id, name, email, phone, status, created_at, updated_at

**Tickets Table**: id, customer_id, issue, status, priority, created_at

The database is automatically created with 15 test customers and 25 test tickets.

## Project Structure

```
assignment5/
├── agents/
│   ├── router_agent.py      # Orchestrator
│   ├── data_agent.py         # Database specialist
│   └── support_agent.py      # Support specialist
├── mcp_server/
│   ├── server.py            # MCP server with 5 tools
│   ├── database.py          # Database operations
│   └── database_setup.py    # DB initialization (instructor provided)
├── main.py                  # Main execution script with testing scenarios
├── comprehensive_test.py    # 21 additional test queries
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── CONCLUSION.md            # Learning outcomes
└── TESTING_RESULTS.md       # Test results (5 scenarios)
```

## A2A Communication

All agent-to-agent communication is logged with timestamps:
```
[2025-11-25 10:30:45] [A2A] RouterAgent → CustomerDataAgent: get_customer
[2025-11-25 10:30:46] [A2A] CustomerDataAgent → RouterAgent: Response: Success
```

## Test Results

All 5 required scenarios pass successfully. Run `python main.py` and choose Option 1 to see full output with A2A coordination logs.

**Optional:** For additional testing with 21 automated queries, run:
```bash
python comprehensive_test.py
```

## Troubleshooting

**Database errors**: Delete `support.db` and re-run (it will be recreated automatically)

**Import errors**: Ensure virtual environment is activated and dependencies are installed


## AI Tool Disclosure
This project was developed with assistance from Claude (Anthropic) for:
- Code structure and debugging
- Documentation and testing strategies
- Best practices in multi-agent system design
All core logic, implementation decisions, and system architecture were designed and understood by me.



## Author
Sumasree Ragi  
Course: Applied Generative AI
University of Chicago