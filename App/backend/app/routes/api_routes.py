"""
API routes - REST API endpoints
"""
from flask import Blueprint, jsonify, request, session
from app.services import CustomerService, BookService, IssueService, AuthService, ExhibitionService
from app.repositories import IssueRepository
from app.utils.decorators import jwt_required, admin_required, get_current_user

api_bp = Blueprint('api', __name__)


# Error handler for API
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Note: Authentication is now handled by @jwt_required decorator on each route
# This allows for more granular control and better error handling


# Customer API
@api_bp.route('/customers', methods=['GET'])
@jwt_required
def get_customers():
    """Get all customers or search"""
    search_term = request.args.get('search', '')
    customers = CustomerService.search_customers(search_term)
    return jsonify([c.to_dict() for c in customers])


@api_bp.route('/customers/<customer_id>', methods=['GET'])
@jwt_required
def get_customer(customer_id):
    """Get customer by ID"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if customer:
        return jsonify(customer.to_dict())
    return jsonify({'error': 'Customer not found'}), 404


@api_bp.route('/customers', methods=['POST'])
@admin_required
def create_customer():
    """Create new customer"""
    data = request.get_json()
    success, message = CustomerService.create_customer(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/customers/<customer_id>', methods=['PUT'])
@admin_required
def update_customer(customer_id):
    """Update customer"""
    data = request.get_json()
    data['id'] = customer_id
    success, message = CustomerService.update_customer(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/customers/<customer_id>', methods=['DELETE'])
@admin_required
def delete_customer(customer_id):
    """Delete customer"""
    success, message = CustomerService.delete_customer(customer_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


# Book API
@api_bp.route('/books', methods=['GET'])
@jwt_required
def get_books():
    """Get all books or search"""
    search_term = request.args.get('search', '')
    available_only = request.args.get('available', 'false').lower() == 'true'
    
    if available_only:
        books = BookService.get_available_books()
    else:
        books = BookService.search_books(search_term)
    
    return jsonify([b.to_dict() for b in books])


@api_bp.route('/books/<book_id>', methods=['GET'])
@jwt_required
def get_book(book_id):
    """Get book by ID"""
    book = BookService.get_book_by_id(book_id)
    if book:
        return jsonify(book.to_dict())
    return jsonify({'error': 'Book not found'}), 404


@api_bp.route('/books', methods=['POST'])
@admin_required
def create_book():
    """Create new book"""
    data = request.get_json()
    success, message = BookService.create_book(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/books/<book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    """Update book"""
    data = request.get_json()
    data['id'] = book_id
    success, message = BookService.update_book(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/books/<book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    """Delete book"""
    success, message = BookService.delete_book(book_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/books/categories', methods=['GET'])
@jwt_required
def get_categories():
    """Get all unique book categories"""
    from app.repositories import BookRepository
    categories = BookRepository.get_all_categories()
    return jsonify(categories)


@api_bp.route('/books/import', methods=['POST'])
@admin_required
def import_books_from_excel():
    """Import books from Excel file"""
    import os
    import tempfile
    from werkzeug.utils import secure_filename
    from app.utils.excel_parser import parse_books_excel
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'}), 400
    
    # Check file extension
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'error': 'Поддерживаются только файлы Excel (.xlsx, .xls)'}), 400
    
    # Save file temporarily
    temp_dir = tempfile.gettempdir()
    temp_filename = secure_filename(file.filename)
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        file.save(temp_path)
        
        # Parse Excel file
        books_data, errors = parse_books_excel(temp_path)
        
        if errors and not books_data:
            return jsonify({
                'success': False,
                'error': 'Ошибки при чтении файла',
                'errors': errors
            }), 400
        
        # Import books
        imported_count = 0
        failed_count = 0
        import_errors = []
        
        for book_data in books_data:
            success, message = BookService.create_book(book_data)
            if success:
                imported_count += 1
            else:
                failed_count += 1
                import_errors.append(f"{book_data.get('title', 'Неизвестная книга')}: {message}")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        result = {
            'success': True,
            'imported': imported_count,
            'failed': failed_count,
            'total': len(books_data)
        }
        
        if import_errors:
            result['errors'] = import_errors[:10]  # Limit errors to first 10
        
        if errors:
            result['parse_errors'] = errors
        
        return jsonify(result)
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'success': False,
            'error': f'Ошибка при обработке файла: {str(e)}'
        }), 500


# Issue API
@api_bp.route('/issues', methods=['GET'])
@jwt_required
def get_issues():
    """Get all issues or search"""
    search_term = request.args.get('search', '')
    status = request.args.get('status', 'all')  # all, active, returned
    customer_id = request.args.get('customer_id')
    
    if customer_id:
        if status == 'active':
            issues = IssueService.get_customer_active_issues(customer_id)
        else:
            issues = IssueService.get_customer_issues(customer_id)
    elif status == 'active':
        issues = IssueService.get_active_issues()
    else:
        issues = IssueService.search_issues(search_term)
    
    return jsonify([i.to_dict() for i in issues])


@api_bp.route('/issues', methods=['POST'])
@jwt_required
def issue_book():
    """Issue a book to a customer (admin can issue to anyone, users can only issue to themselves)"""
    data = request.get_json()
    book_id = data.get('book_id')
    customer_id = data.get('customer_id')
    
    if not book_id or not customer_id:
        return jsonify({'success': False, 'error': 'Book ID and Customer ID are required'}), 400
    
    # Check if user is trying to issue book to themselves (for regular users)
    current_user = get_current_user()
    if not current_user:
        return jsonify({'success': False, 'error': 'Требуется авторизация'}), 401
    
    # Regular users can only issue books to themselves
    if current_user.get('role') != 'admin':
        if current_user.get('customer_id') != customer_id:
            return jsonify({'success': False, 'error': 'Вы можете взять книгу только для себя'}), 403
    
    success, message = IssueService.issue_book(book_id, customer_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/issues/<int:issue_id>/return', methods=['POST'])
@jwt_required
def return_book(issue_id):
    """Return a book (admin can return any book, users can only return their own)"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'success': False, 'error': 'Требуется авторизация'}), 401
    
    # Regular users can only return their own books
    if current_user.get('role') != 'admin':
        issue = IssueRepository.find_by_id(issue_id)
        if not issue:
            return jsonify({'success': False, 'error': 'Выдача не найдена'}), 404
        if issue.customer_id != current_user.get('customer_id'):
            return jsonify({'success': False, 'error': 'Вы можете вернуть только свои книги'}), 403
    
    success, message = IssueService.return_book(issue_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


# Statistics and Reports API
@api_bp.route('/statistics', methods=['GET'])
@jwt_required
def get_statistics():
    """Get library statistics"""
    stats = IssueService.get_statistics()
    return jsonify(stats)


@api_bp.route('/reports/full', methods=['GET'])
@admin_required
def get_full_report():
    """Get full report"""
    report = IssueService.generate_full_report()
    return jsonify(report)


@api_bp.route('/reports/overdue', methods=['GET'])
@admin_required
def get_overdue_report():
    """Get overdue books report"""
    report = IssueService.generate_overdue_report()
    return jsonify(report)


# User Profile API
@api_bp.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    """Get current user profile"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Требуется авторизация'}), 401
    
    success, profile, message = AuthService.get_user_profile(current_user['id'])
    if success:
        return jsonify(profile)
    return jsonify({'error': message}), 404


@api_bp.route('/profile', methods=['PUT'])
@jwt_required
def update_profile():
    """Update current user profile"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'success': False, 'error': 'Требуется авторизация'}), 401
    
    data = request.get_json()
    success, message = AuthService.update_user_profile(current_user['id'], data)
    
    if success:
        # Get updated profile
        _, updated_profile, _ = AuthService.get_user_profile(current_user['id'])
        
        # Generate new JWT token if name or email changed
        user = AuthService.get_user_by_id(current_user['id'])
        if user:
            new_token = AuthService.generate_user_token(user)
            return jsonify({
                'success': True,
                'message': message,
                'profile': updated_profile,
                'token': new_token
            })
        
        return jsonify({
            'success': True,
            'message': message,
            'profile': updated_profile
        })
    return jsonify({'success': False, 'error': message}), 400


# Exhibition API
@api_bp.route('/exhibitions', methods=['GET'])
@jwt_required
def get_exhibitions():
    """Get all exhibitions (admin) or active exhibitions (user)"""
    current_user = get_current_user()
    if current_user and current_user.get('role') == 'admin':
        exhibitions = ExhibitionService.get_all_exhibitions()
    else:
        exhibitions = ExhibitionService.get_active_exhibitions()
    
    result = []
    for exhibition in exhibitions:
        ex_dict = exhibition.to_dict()
        # Include books for active exhibitions
        if exhibition.is_currently_active():
            books = ExhibitionService.get_exhibition_with_books(exhibition.id)
            if books:
                ex_dict['books'] = books['books']
        result.append(ex_dict)
    
    return jsonify(result)


@api_bp.route('/exhibitions/active', methods=['GET'])
def get_active_exhibitions():
    """Get active exhibitions (public endpoint for users)"""
    exhibitions = ExhibitionService.get_active_exhibitions()
    result = []
    for exhibition in exhibitions:
        ex_dict = exhibition.to_dict()
        books = ExhibitionService.get_exhibition_with_books(exhibition.id)
        if books:
            ex_dict['books'] = books['books']
        result.append(ex_dict)
    return jsonify(result)


@api_bp.route('/exhibitions/<int:exhibition_id>', methods=['GET'])
@jwt_required
def get_exhibition(exhibition_id):
    """Get exhibition by ID with books"""
    exhibition_data = ExhibitionService.get_exhibition_with_books(exhibition_id)
    if exhibition_data:
        return jsonify(exhibition_data)
    return jsonify({'error': 'Exhibition not found'}), 404


@api_bp.route('/exhibitions', methods=['POST'])
@admin_required
def create_exhibition():
    """Create new exhibition"""
    data = request.get_json()
    success, message, exhibition_id = ExhibitionService.create_exhibition(data)
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'exhibition_id': exhibition_id
        })
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/exhibitions/<int:exhibition_id>', methods=['PUT'])
@admin_required
def update_exhibition(exhibition_id):
    """Update exhibition"""
    data = request.get_json()
    data['id'] = exhibition_id
    success, message = ExhibitionService.update_exhibition(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/exhibitions/<int:exhibition_id>', methods=['DELETE'])
@admin_required
def delete_exhibition(exhibition_id):
    """Delete exhibition"""
    success, message = ExhibitionService.delete_exhibition(exhibition_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/exhibitions/<int:exhibition_id>/toggle', methods=['POST'])
@admin_required
def toggle_exhibition(exhibition_id):
    """Toggle exhibition active status"""
    success, message = ExhibitionService.toggle_exhibition_status(exhibition_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/exhibitions/<int:exhibition_id>/books', methods=['POST'])
@admin_required
def add_book_to_exhibition(exhibition_id):
    """Add a book to an exhibition"""
    data = request.get_json()
    book_id = data.get('book_id')
    display_order = data.get('display_order', 0)
    
    if not book_id:
        return jsonify({'success': False, 'error': 'Book ID is required'}), 400
    
    success, message = ExhibitionService.add_book_to_exhibition(exhibition_id, book_id, display_order)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/exhibitions/<int:exhibition_id>/books/<book_id>', methods=['DELETE'])
@admin_required
def remove_book_from_exhibition(exhibition_id, book_id):
    """Remove a book from an exhibition"""
    success, message = ExhibitionService.remove_book_from_exhibition(exhibition_id, book_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/exhibitions/<int:exhibition_id>/books/order', methods=['PUT'])
@admin_required
def update_exhibition_book_order(exhibition_id):
    """Update display order of books in an exhibition"""
    data = request.get_json()
    book_orders = data.get('book_orders', [])
    
    if not book_orders:
        return jsonify({'success': False, 'error': 'Book orders are required'}), 400
    
    success, message = ExhibitionService.update_book_order(exhibition_id, book_orders)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400

