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
    def get_statistics() -> dict:
        """Get statistics about issues"""
        stats = IssueRepository.get_statistics()
        
        # Add customer count
        customers = CustomerRepository.find_all()
        stats['total_customers'] = len(customers)
        
        # Add book count
        books = BookRepository.find_all()
        stats['total_books'] = len(books)
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
        overdue_issues = IssueService.get_overdue_issues()
        
        report = []
        for issue in overdue_issues:
            report.append({
                'issue_id': issue.id,
                'book_title': issue.book_title,
                'customer_name': issue.customer_name,
                'date_issued': issue.date_issued,
                'days_borrowed': issue.days_borrowed,
                'days_overdue': issue.days_borrowed - LOAN_PERIOD_DAYS
            })
        
        return report


