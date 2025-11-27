import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

class CustomerDatabase:
    """
    Database operations for customer service system.
    Provides methods for all MCP tools.
    """
    
    def __init__(self, db_path="support.db"):
        self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Get customer information by ID.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dictionary with customer information or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, phone, status, created_at, updated_at
            FROM customers
            WHERE id = ?
        """, (customer_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list_customers(self, status: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List customers with optional status filter.
        
        Args:
            status: Filter by status ('active' or 'disabled'). None for all.
            limit: Maximum number of customers to return
            
        Returns:
            List of customer dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM customers
                WHERE status = ?
                LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM customers
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> bool:
        """
        Update customer information.
        
        Args:
            customer_id: Customer ID
            data: Dictionary with fields to update (name, email, phone, status)
            
        Returns:
            True if successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query based on provided fields
        allowed_fields = ['name', 'email', 'phone', 'status']
        update_fields = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                values.append(data[field])
        
        if not update_fields:
            conn.close()
            return False
        
        # Always update updated_at
        update_fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        
        # Add customer_id to values
        values.append(customer_id)
        
        query = f"""
            UPDATE customers
            SET {', '.join(update_fields)}
            WHERE id = ?
        """
        
        try:
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"Error updating customer: {e}")
            conn.close()
            return False
    
    def create_ticket(self, customer_id: int, issue: str, priority: str = "medium") -> Optional[int]:
        """
        Create a new support ticket.
        
        Args:
            customer_id: Customer ID
            issue: Description of the issue
            priority: Priority level ('low', 'medium', 'high')
            
        Returns:
            Ticket ID if successful, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Verify customer exists
        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if not cursor.fetchone():
            conn.close()
            return None
        
        try:
            cursor.execute("""
                INSERT INTO tickets (customer_id, issue, status, priority)
                VALUES (?, ?, 'open', ?)
            """, (customer_id, issue, priority))
            
            conn.commit()
            ticket_id = cursor.lastrowid
            conn.close()
            return ticket_id
        except sqlite3.Error as e:
            print(f"Error creating ticket: {e}")
            conn.close()
            return None
    
    def get_customer_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """
        Get all tickets for a customer.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List of ticket dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, customer_id, issue, status, priority, created_at
            FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """, (customer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_tickets_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """
        Get all tickets by priority.
        
        Args:
            priority: Priority level ('low', 'medium', 'high')
            
        Returns:
            List of ticket dictionaries with customer info
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.customer_id, t.issue, t.status, t.priority, t.created_at,
                   c.name as customer_name, c.email as customer_email
            FROM tickets t
            JOIN customers c ON t.customer_id = c.id
            WHERE t.priority = ?
            ORDER BY t.created_at DESC
        """, (priority,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_tickets_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all tickets by status.
        
        Args:
            status: Ticket status ('open', 'in_progress', 'resolved')
            
        Returns:
            List of ticket dictionaries with customer info
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.customer_id, t.issue, t.status, t.priority, t.created_at,
                   c.name as customer_name, c.email as customer_email, c.status as customer_status
            FROM tickets t
            JOIN customers c ON t.customer_id = c.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
        """, (status,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]