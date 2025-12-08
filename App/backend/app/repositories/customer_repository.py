"""
Customer Repository - Data access layer for customers
"""
from typing import List, Optional
from app.database import get_db_connection
from app.models import Customer
from psycopg2.extras import RealDictCursor


class CustomerRepository:
    """Repository for customer data access"""
    
    @staticmethod
    def find_all() -> List[Customer]:
        """Get all customers"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM customers ORDER BY name')
            rows = cursor.fetchall()
            return [Customer.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(customer_id: str) -> Optional[Customer]:
        """Find customer by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM customers WHERE id = %s', (customer_id,))
            row = cursor.fetchone()
            return Customer.from_dict(dict(row)) if row else None
    
    @staticmethod
    def search(search_term: str) -> List[Customer]:
        """Search customers by ID, name, or email"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = '''
                SELECT * FROM customers
                WHERE id LIKE %s OR name LIKE %s OR email LIKE %s
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
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                    SET name=%s, address=%s, zip=%s, city=%s, phone=%s, email=%s
                    WHERE id=%s
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
                cursor.execute('DELETE FROM customers WHERE id = %s', (customer_id,))
                return True
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False
    
    @staticmethod
    def generate_unique_id() -> str:
        """Generate a unique customer ID in format C####"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Get all customer IDs that start with 'C'
            cursor.execute("SELECT id FROM customers WHERE id LIKE %s", ('C%',))
            rows = cursor.fetchall()
            
            if rows:
                # Extract numbers from existing IDs and find the maximum
                max_num = 0
                for row in rows:
                    existing_id = row[0]
                    try:
                        # Extract number part (skip 'C' prefix)
                        num = int(existing_id[1:])
                        if num > max_num:
                            max_num = num
                    except ValueError:
                        continue
                new_num = max_num + 1
            else:
                new_num = 1
            
            # Format as C#### (4 digits)
            new_id = f"C{new_num:04d}"
            
            # Ensure uniqueness (in case of gaps or conflicts)
            while CustomerRepository.find_by_id(new_id):
                new_num += 1
                new_id = f"C{new_num:04d}"
            
            return new_id


