"""
Routes package
"""
from app.routes.main_routes import main_bp
from app.routes.admin_routes import admin_bp
from app.routes.user_routes import user_bp
from app.routes.api_routes import api_bp

__all__ = ['main_bp', 'admin_bp', 'user_bp', 'api_bp']


