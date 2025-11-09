"""
Authentication routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        success, user, message = AuthService.login(email, password)
        
        if success:
            # Store user info in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            session['user_name'] = user.name
            session['customer_id'] = user.customer_id
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash(message, 'danger')
            return render_template('auth/login.html', error=message)
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('auth/register.html', error='Пароли не совпадают')
        
        success, user, message = AuthService.register(email, password, name)
        
        if success:
            flash('Регистрация успешна! Войдите в систему.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
            return render_template('auth/register.html', error=message)
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))








