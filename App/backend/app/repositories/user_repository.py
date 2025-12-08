"""
User Repository - Data access layer for users
"""
from typing import Optional
from app.database import get_db_connection
from app.models import User
from psycopg2.extras import RealDictCursor


class UserRepository:
    """Repository for user data access"""
    
    @staticmethod
    def find_by_email(email: str) -> Optional[User]:
        """Find user by email"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None
    
    @staticmethod
    def find_by_id(user_id: int) -> Optional[User]:
        """Find user by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
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
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    user.email,
                    user.password_hash,
                    user.role,
                    user.customer_id,
                    user.name
                ))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if email already exists"""
        user = UserRepository.find_by_email(email)
        return user is not None
    
    @staticmethod
    def update(user: User) -> bool:
        """Update user"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users
                    SET email=%s, password_hash=%s, name=%s
                    WHERE id=%s
                ''', (
                    user.email,
                    user.password_hash,
                    user.name,
                    user.id
                ))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def email_exists_for_other_user(email: str, exclude_user_id: int) -> bool:
        """Check if email exists for another user"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE email = %s AND id != %s', (email, exclude_user_id))
            row = cursor.fetchone()
            return row is not None








