"""
Issue Service - Business logic for book issue (loan) operations
"""
from typing import List, Optional
from datetime import datetime
from app.models import Issue
from app.repositories import IssueRepository, BookRepository, CustomerRepository
from config import LOAN_PERIOD_DAYS, MAX_BOOKS_PER_USER


class IssueService:
    """Service for book issue business logic"""
    
    @staticmethod
    def get_all_issues() -> List[Issue]:
        """Get all issues"""
        return IssueRepository.find_all()
    
    @staticmethod
    def get_active_issues() -> List[Issue]:
        """Get all active issues"""
        return IssueRepository.find_active()
    
    @staticmethod
    def get_returned_issues() -> List[Issue]:
        """Get all returned issues"""
        return IssueRepository.find_returned()
    
    @staticmethod
    def get_customer_issues(customer_id: str) -> List[Issue]:
        """Get all issues for a customer"""
        return IssueRepository.find_by_customer(customer_id)
    
    @staticmethod
    def get_customer_active_issues(customer_id: str) -> List[Issue]:
        """Get active issues for a customer"""
        return IssueRepository.find_active_by_customer(customer_id)
    
    @staticmethod
    def search_issues(search_term: str) -> List[Issue]:
        """Search issues"""
        if not search_term:
            return IssueRepository.find_all()
        return IssueRepository.search(search_term)
    
    @staticmethod
    def issue_book(book_id: str, customer_id: str) -> tuple[bool, str]:
        """
        Issue a book to a customer
        Returns: (success: bool, message: str)
        """
        # Validate book exists
        book = BookRepository.find_by_id(book_id)
        if not book:
            return False, "Book not found"
        
        # Check if book is available
        if not book.is_available:
            return False, "Book is not available"
        
        # Validate customer exists
        customer = CustomerRepository.find_by_id(customer_id)
        if not customer:
            return False, "Customer not found"
        
        # Check if customer has reached maximum books
        active_issues = IssueRepository.find_active_by_customer(customer_id)
        if len(active_issues) >= MAX_BOOKS_PER_USER:
            return False, f"Customer has reached maximum limit of {MAX_BOOKS_PER_USER} books"
        
        # Create issue
        issue = Issue(
            id=None,
            book_id=book.id,
            book_title=book.title,
            customer_id=customer.id,
            customer_name=customer.name,
            date_issued=datetime.now().strftime('%Y-%m-%d'),
            status='issued'
        )
        
        issue_id = IssueRepository.create(issue)
        if not issue_id:
            return False, "Failed to create issue"
        
        # Decrease available copies
        if not BookRepository.decrease_available_copies(book_id):
            return False, "Failed to update book availability"
        
        return True, "Book issued successfully"
    
    @staticmethod
    def return_book(issue_id: int) -> tuple[bool, str]:
        """
        Return a book
        Returns: (success: bool, message: str)
        """
        # Get issue
        issue = IssueRepository.find_by_id(issue_id)
        if not issue:
            return False, "Issue not found"
        
        # Check if already returned
        if issue.status == 'returned':
            return False, "Book has already been returned"
        
        # Return book
        if not IssueRepository.return_book(issue_id):
            return False, "Failed to return book"
        
        # Increase available copies
        if not BookRepository.increase_available_copies(issue.book_id):
            return False, "Failed to update book availability"
        
        return True, "Book returned successfully"
    
    @staticmethod
    def get_overdue_issues() -> List[Issue]:
        """Get all overdue issues"""
        return IssueRepository.get_overdue()
    
    @staticmethod
    def extend_issue(issue_id: int) -> tuple[bool, str]:
        """
        Extend an issue by 7 days (one week)
        Returns: (success: bool, message: str)
        """
        # Check if issue exists and is active
        issue = IssueRepository.find_by_id(issue_id)
        if not issue:
            return False, "Выдача не найдена"
        
        if issue.status != 'issued':
            return False, "Можно продлить только активную выдачу"
        
        if issue.extended:
            return False, "Выдача уже была продлена. Продление возможно только один раз"
        
        # Extend the issue
        success, message = IssueRepository.extend_issue(issue_id)
        return success, message
    
    @staticmethod
    def get_statistics() -> dict:
        """Get statistics about issues"""
        stats = IssueRepository.get_statistics()
        
        # Add customer count
        customers = CustomerRepository.find_all()
        stats['total_customers'] = len(customers)
        
        # Add book count
        books, total_books_count = BookRepository.find_all()
        stats['total_books'] = total_books_count
        stats['available_books'] = len([b for b in books if b.is_available])
        
        # Overdue count is already calculated in IssueRepository.get_statistics()
        # using SQL query for accuracy
        
        return stats
    
    @staticmethod
    def generate_full_report() -> dict:
        """Generate comprehensive report"""
        stats = IssueService.get_statistics()
        active_issues = IssueRepository.find_active()
        overdue_issues = IssueService.get_overdue_issues()
        
        return {
            'statistics': stats,
            'active_issues': [issue.to_dict() for issue in active_issues],
            'overdue_issues': [issue.to_dict() for issue in overdue_issues]
        }
    
    @staticmethod
    def generate_overdue_report() -> List[dict]:
        """Generate overdue books report"""
        from datetime import datetime, timedelta
        from config import LOAN_PERIOD_DAYS, SYSTEM_DATE, USE_SYSTEM_DATE
        
        overdue_issues = IssueService.get_overdue_issues()
        
        report = []
        for issue in overdue_issues:
            # Calculate return date (date_issued + LOAN_PERIOD_DAYS)
            try:
                if isinstance(issue.date_issued, str):
                    issued_date = datetime.strptime(issue.date_issued, '%Y-%m-%d')
                else:
                    issued_date = datetime.combine(issue.date_issued, datetime.min.time())
                
                return_date = issued_date + timedelta(days=LOAN_PERIOD_DAYS)
                return_date_str = return_date.strftime('%Y-%m-%d')
            except:
                return_date_str = 'Не указана'
            
            report.append({
                'issue_id': issue.id,
                'book_title': issue.book_title,
                'customer_name': issue.customer_name,
                'date_issued': issue.date_issued,
                'return_date': return_date_str,  # New column: "Вернуть до"
                'days_borrowed': issue.days_borrowed,
                'days_overdue': issue.days_borrowed - LOAN_PERIOD_DAYS
            })
        
        return report
    
    @staticmethod
    def create_issue_from_import(issue_data: dict) -> tuple[bool, str]:
        """
        Create an issue from imported data (for Excel import)
        Returns: (success: bool, message: str)
        """
        # Validate required fields
        if not issue_data.get('book_id'):
            return False, "Book ID is required"
        if not issue_data.get('customer_id'):
            return False, "Customer ID is required"
        if not issue_data.get('date_issued'):
            return False, "Date of issue is required"
        
        # Validate book exists
        book = BookRepository.find_by_id(issue_data['book_id'])
        if not book:
            return False, f"Book with ID '{issue_data['book_id']}' not found"
        
        # Use book title from database if not provided in import
        book_title = issue_data.get('book_title') or book.title
        
        # Validate customer exists
        customer = CustomerRepository.find_by_id(issue_data['customer_id'])
        if not customer:
            return False, f"Customer with ID '{issue_data['customer_id']}' not found"
        
        # Use customer name from database if not provided in import
        customer_name = issue_data.get('customer_name') or customer.name
        
        # Determine status
        status = issue_data.get('status', 'issued')
        date_return = issue_data.get('date_return')
        
        # If status is 'issued', check if book is available
        if status == 'issued':
            # Check if book has available copies
            if book.available_copies <= 0:
                return False, f"Book '{book_title}' is not available (no copies left)"
        
        # Create issue
        issue = Issue(
            id=None,
            book_id=issue_data['book_id'],
            book_title=book_title,
            customer_id=issue_data['customer_id'],
            customer_name=customer_name,
            date_issued=issue_data['date_issued'],
            date_return=date_return,
            status=status
        )
        
        issue_id = IssueRepository.create(issue)
        if not issue_id:
            return False, "Failed to create issue"
        
        # Update book availability only if status is 'issued'
        if status == 'issued':
            if not BookRepository.decrease_available_copies(issue_data['book_id']):
                # Rollback: delete the issue we just created
                IssueRepository.delete(issue_id)
                return False, "Failed to update book availability"
        
        return True, f"Issue created successfully (ID: {issue_id})"


