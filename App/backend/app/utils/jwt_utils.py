"""
JWT utilities for token generation and validation
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS


def generate_token(user_id: int, email: str, role: str, customer_id: Optional[str] = None, name: str = "") -> str:
    """
    Generate JWT token for user
    
    Args:
        user_id: User ID
        email: User email
        role: User role ('admin' or 'user')
        customer_id: Customer ID (for regular users)
        name: User name
    
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'customer_id': customer_id,
        'name': name,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    # PyJWT 2.x returns string directly, but ensure it's a string
    return str(token)


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_header(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract token from Authorization header
    
    Args:
        auth_header: Authorization header value (format: "Bearer <token>")
    
    Returns:
        Token string if valid format, None otherwise
    """
    if not auth_header:
        return None
    
    try:
        scheme, token = auth_header.split(' ')
        if scheme.lower() != 'bearer':
            return None
        return token
    except ValueError:
        return None

