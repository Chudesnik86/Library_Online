"""
Admin routes - Pages for administrator
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.utils.jwt_utils import verify_token, get_token_from_header

admin_bp = Blueprint('admin', __name__)


def require_admin():
    """Check if user is logged in and is admin (supports both JWT and session)"""
    # Try JWT token first
    auth_header = request.headers.get('Authorization')
    token = get_token_from_header(auth_header)
    
    if token:
        payload = verify_token(token)
        if payload and payload.get('role') == 'admin':
            # Set session from JWT for template compatibility
            session['user_id'] = payload.get('user_id')
            session['user_email'] = payload.get('email')
            session['user_role'] = payload.get('role')
            session['user_name'] = payload.get('name')
            session['customer_id'] = payload.get('customer_id')
            return None
    
    # Fallback to session
    if 'user_id' not in session:
        flash('Требуется авторизация', 'warning')
        return redirect(url_for('auth.login'))
    if session.get('user_role') != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('user.dashboard'))
    return None


@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    return render_template('admin/dashboard.html', user_name=session.get('user_name'))


@admin_bp.route('/customers')
def customers():
    """Manage customers"""
    redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    return render_template('admin/customers.html', user_name=session.get('user_name'))


@admin_bp.route('/books')
def books():
    """Manage books"""
    redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    return render_template('admin/books.html', user_name=session.get('user_name'))


@admin_bp.route('/issues')
def issues():
    """Manage book issues"""
    redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    return render_template('admin/issues.html', user_name=session.get('user_name'))


@admin_bp.route('/reports')
def reports():
    """View reports"""
    redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    return render_template('admin/reports.html', user_name=session.get('user_name'))


@admin_bp.route('/exhibitions')
def exhibitions():
    """Manage exhibitions"""
    redirect_response = require_admin()
    if redirect_response:
        return redirect_response
    return render_template('admin/exhibitions.html', user_name=session.get('user_name'))

