"""
API routes - REST API endpoints
"""
from flask import Blueprint, jsonify, request, session
from app.services import CustomerService, BookService, IssueService

api_bp = Blueprint('api', __name__)


# Error handler for API
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Middleware to check authentication for API calls
@api_bp.before_request
def check_auth():
    """Check if user is logged in for API requests"""
    if 'user_id' not in session:
        return jsonify({'error': 'Требуется авторизация'}), 401


# Customer API
@api_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers or search"""
    search_term = request.args.get('search', '')
    customers = CustomerService.search_customers(search_term)
    return jsonify([c.to_dict() for c in customers])


@api_bp.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer by ID"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if customer:
        return jsonify(customer.to_dict())
    return jsonify({'error': 'Customer not found'}), 404


@api_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create new customer"""
    data = request.get_json()
    success, message = CustomerService.create_customer(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer"""
    data = request.get_json()
    data['id'] = customer_id
    success, message = CustomerService.update_customer(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/customers/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete customer"""
    success, message = CustomerService.delete_customer(customer_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


# Book API
@api_bp.route('/books', methods=['GET'])
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
def get_book(book_id):
    """Get book by ID"""
    book = BookService.get_book_by_id(book_id)
    if book:
        return jsonify(book.to_dict())
    return jsonify({'error': 'Book not found'}), 404


@api_bp.route('/books', methods=['POST'])
def create_book():
    """Create new book"""
    data = request.get_json()
    success, message = BookService.create_book(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """Update book"""
    data = request.get_json()
    data['id'] = book_id
    success, message = BookService.update_book(data)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete book"""
    success, message = BookService.delete_book(book_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


# Issue API
@api_bp.route('/issues', methods=['GET'])
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
def issue_book():
    """Issue a book to a customer"""
    data = request.get_json()
    book_id = data.get('book_id')
    customer_id = data.get('customer_id')
    
    if not book_id or not customer_id:
        return jsonify({'success': False, 'error': 'Book ID and Customer ID are required'}), 400
    
    success, message = IssueService.issue_book(book_id, customer_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


@api_bp.route('/issues/<int:issue_id>/return', methods=['POST'])
def return_book(issue_id):
    """Return a book"""
    success, message = IssueService.return_book(issue_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400


# Statistics and Reports API
@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get library statistics"""
    stats = IssueService.get_statistics()
    return jsonify(stats)


@api_bp.route('/reports/full', methods=['GET'])
def get_full_report():
    """Get full report"""
    report = IssueService.generate_full_report()
    return jsonify(report)


@api_bp.route('/reports/overdue', methods=['GET'])
def get_overdue_report():
    """Get overdue books report"""
    report = IssueService.generate_overdue_report()
    return jsonify(report)

