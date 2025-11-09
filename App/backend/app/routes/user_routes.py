"""
User routes - Pages for regular users
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

user_bp = Blueprint('user', __name__)


def require_user():
    """Check if user is logged in"""
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
    """Browse available books"""
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    return render_template('user/browse_books.html', 
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

