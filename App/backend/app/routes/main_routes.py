"""
Main routes - Homepage
"""
from flask import Blueprint, redirect, url_for, session

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage - redirect to login or dashboard"""
    if 'user_id' in session:
        # User is logged in, redirect based on role
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    else:
        # Not logged in, redirect to login
        return redirect(url_for('auth.login'))

