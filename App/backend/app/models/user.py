"""
User model for authentication
"""
from dataclasses import dataclass
from typing import Optional
import hashlib


@dataclass
class User:
    """User entity for authentication"""
    id: Optional[int]
    email: str
    password_hash: str
    role: str  # 'admin' or 'user'
    customer_id: Optional[str] = None  # Link to customer for regular users
    name: str = ""
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create User from dictionary"""
        return cls(
            id=data.get('id'),
            email=data['email'],
            password_hash=data['password_hash'],
            role=data.get('role', 'user'),
            customer_id=data.get('customer_id'),
            name=data.get('name', '')
        )
    
    def to_dict(self):
        """Convert User to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'customer_id': self.customer_id,
            'name': self.name
        }
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if password is correct"""
        return self.password_hash == User.hash_password(password)








