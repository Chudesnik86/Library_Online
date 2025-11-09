"""
Customer Repository - Data access layer for customers
"""
from typing import List, Optional
from app.database import get_db_connection
from app.models import Customer


class CustomerRepository:
    """Repository for customer data access"""
    
    @staticmethod
    def find_all() -> List[Customer]:
        """Get all customers"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers ORDER BY name')
            rows = cursor.fetchall()
            return [Customer.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(customer_id: str) -> Optional[Customer]:
        """Find customer by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            row = cursor.fetchone()
            return Customer.from_dict(dict(row)) if row else None
    
    @staticmethod
    def search(search_term: str) -> List[Customer]:
        """Search customers by ID, name, or email"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM customers
                WHERE id LIKE ? OR name LIKE ? OR email LIKE ?
                ORDER BY name
            '''
            pattern = f'%{search_term}%'
            cursor.execute(query, (pattern, pattern, pattern))
            rows = cursor.fetchall()
            return [Customer.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def create(customer: Customer) -> bool:
        """Create a new customer"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO customers (id, name, address, zip, city, phone, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    customer.id,
                    customer.name,
                    customer.address,
                    customer.zip,
                    customer.city,
                    customer.phone,
                    customer.email
                ))
                return True
        except Exception as e:
            print(f"Error creating customer: {e}")
            return False
    
    @staticmethod
    def update(customer: Customer) -> bool:
        """Update customer"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE customers
                    SET name=?, address=?, zip=?, city=?, phone=?, email=?
                    WHERE id=?
                ''', (
                    customer.name,
                    customer.address,
                    customer.zip,
                    customer.city,
                    customer.phone,
                    customer.email,
                    customer.id
                ))
                return True
        except Exception as e:
            print(f"Error updating customer: {e}")
            return False
    
    @staticmethod
    def delete(customer_id: str) -> bool:
        """Delete customer"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
                return True
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False


