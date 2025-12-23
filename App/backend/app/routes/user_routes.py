"""
User routes - Pages for regular users
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.utils.jwt_utils import verify_token, get_token_from_header

user_bp = Blueprint('user', __name__)


def require_user():
    """Check if user is logged in (supports both JWT and session)"""
    # Try JWT token first
    auth_header = request.headers.get('Authorization')
    token = get_token_from_header(auth_header)
    
    if token:
        payload = verify_token(token)
        if payload:
            # Set session from JWT for template compatibility
            session['user_id'] = payload.get('user_id')
            session['user_email'] = payload.get('email')
            session['user_role'] = payload.get('role')
            session['user_name'] = payload.get('name')
            session['customer_id'] = payload.get('customer_id')
            if not session.get('customer_id'):
                flash('Ошибка профиля пользователя', 'danger')
                return redirect(url_for('auth.login'))
            return None
    
    # Fallback to session
    if 'user_id' not in session:
        flash('Требуется авторизация', 'warning')
        return redirect(url_for('auth.login'))
    if not session.get('customer_id'):
        flash('Ошибка профиля пользователя', 'danger')
        return redirect(url_for('auth.login'))
    return None


@user_bp.route('/')
@user_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    return render_template('user/dashboard.html', 
                         customer_id=session.get('customer_id'),
                         user_name=session.get('user_name'))


@user_bp.route('/browse_books')
def browse_books():
    """Browse available books (available for unauthenticated users)"""
    # Allow both authenticated and unauthenticated users to browse books
    # customer_id and user_name will be None for unauthenticated users
    return render_template('user/browse_books.html', 
                         customer_id=session.get('customer_id'),
                         user_name=session.get('user_name'))


@user_bp.route('/exhibitions')
def exhibitions():
    """View exhibitions (available for unauthenticated users)"""
    # Allow both authenticated and unauthenticated users to view exhibitions
    return render_template('user/exhibitions.html', 
                         customer_id=session.get('customer_id'),
                         user_name=session.get('user_name'))


@user_bp.route('/my_books')
def my_books():
    """View borrowed books"""
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    return render_template('user/my_books.html', 
                         customer_id=session.get('customer_id'),
                         user_name=session.get('user_name'))


@user_bp.route('/profile')
def profile():
    """User profile page"""
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    return render_template('user/profile.html', 
                         customer_id=session.get('customer_id'),
                         user_name=session.get('user_name'))

