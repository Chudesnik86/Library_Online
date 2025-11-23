"""
Authentication routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.services import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        # Check if it's an API request (JSON)
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')
        
        success, user, message = AuthService.login(email, password)
        
        if success:
            # Generate JWT token
            token = AuthService.generate_user_token(user)
            
            # Store user info in session (for backward compatibility)
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            session['user_name'] = user.name
            session['customer_id'] = user.customer_id
            
            # If API request, return JSON with token
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': message,
                    'token': token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'name': user.name,
                        'customer_id': user.customer_id
                    }
                })
            
            # For HTML form, store token in session and redirect
            session['jwt_token'] = token
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            # If API request, return JSON error
            if request.is_json:
                return jsonify({'success': False, 'error': message}), 401
            
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


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout"""
    # Clear session
    session.clear()
    
    # If API request, return JSON
    if request.is_json or request.method == 'POST':
        return jsonify({'success': True, 'message': 'Вы вышли из системы'})
    
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/verify', methods=['GET', 'POST'])
def verify_token():
    """Verify JWT token endpoint"""
    from app.utils.jwt_utils import verify_token, get_token_from_header
    
    auth_header = request.headers.get('Authorization')
    token = get_token_from_header(auth_header)
    
    if not token:
        return jsonify({'valid': False, 'error': 'Token not provided'}), 401
    
    payload = verify_token(token)
    if payload:
        return jsonify({
            'valid': True,
            'user': {
                'id': payload.get('user_id'),
                'email': payload.get('email'),
                'role': payload.get('role'),
                'name': payload.get('name'),
                'customer_id': payload.get('customer_id')
            }
        })
    else:
        return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 401


@auth_bp.route('/api/token', methods=['GET'])
def get_token_from_session():
    """Get JWT token from session (for backward compatibility with form login)"""
    if 'jwt_token' in session:
        return jsonify({'token': session['jwt_token']})
    return jsonify({'token': None}), 404








