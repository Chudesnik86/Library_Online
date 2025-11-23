"""
Decorators for authentication and authorization
"""
from functools import wraps
from flask import request, jsonify, session
from app.utils.jwt_utils import verify_token, get_token_from_header
from app.services import AuthService


def jwt_required(f):
    """
    Decorator to require JWT token authentication
    Falls back to session if JWT token is not provided (for backward compatibility)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try to get token from Authorization header
        auth_header = request.headers.get('Authorization')
        token = get_token_from_header(auth_header)
        
        if token:
            # Verify JWT token
            payload = verify_token(token)
            if payload:
                # Add user info to request context
                request.current_user = {
                    'id': payload.get('user_id'),
                    'email': payload.get('email'),
                    'role': payload.get('role'),
                    'name': payload.get('name'),
                    'customer_id': payload.get('customer_id')
                }
                return f(*args, **kwargs)
            else:
                return jsonify({'error': 'Invalid or expired token'}), 401
        else:
            # Fallback to session-based authentication
            if 'user_id' in session:
                request.current_user = {
                    'id': session.get('user_id'),
                    'email': session.get('user_email'),
                    'role': session.get('user_role'),
                    'name': session.get('user_name'),
                    'customer_id': session.get('customer_id')
                }
                return f(*args, **kwargs)
            else:
                return jsonify({'error': 'Требуется авторизация'}), 401
    
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role
    """
    @wraps(f)
    @jwt_required
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or request.current_user.get('role') != 'admin':
            return jsonify({'error': 'Доступ запрещен. Требуются права администратора'}), 403
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    Helper function to get current user from request context or session
    """
    if hasattr(request, 'current_user'):
        return request.current_user
    
    # Fallback to session
    if 'user_id' in session:
        return {
            'id': session.get('user_id'),
            'email': session.get('user_email'),
            'role': session.get('user_role'),
            'name': session.get('user_name'),
            'customer_id': session.get('customer_id')
        }
    
    return None

