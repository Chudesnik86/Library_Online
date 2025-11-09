"""
User Repository - Data access layer for users
"""
from typing import Optional
from app.database import get_db_connection
from app.models import User


class UserRepository:
    """Repository for user data access"""
    
    @staticmethod
    def find_by_email(email: str) -> Optional[User]:
        """Find user by email"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None
    
    @staticmethod
    def find_by_id(user_id: int) -> Optional[User]:
        """Find user by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None
    
    @staticmethod
    def create(user: User) -> Optional[int]:
        """Create a new user"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (email, password_hash, role, customer_id, name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user.email,
                    user.password_hash,
                    user.role,
                    user.customer_id,
                    user.name
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if email already exists"""
        user = UserRepository.find_by_email(email)
        return user is not None








