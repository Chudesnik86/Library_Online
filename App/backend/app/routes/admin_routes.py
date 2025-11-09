"""
Admin routes - Pages for administrator
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

admin_bp = Blueprint('admin', __name__)


def require_admin():
    """Check if user is logged in and is admin"""
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

