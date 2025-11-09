"""
Book Service - Business logic for book operations
"""
from typing import List, Optional
from app.models import Book
from app.repositories import BookRepository


class BookService:
    """Service for book business logic"""
    
    @staticmethod
    def get_all_books() -> List[Book]:
        """Get all books"""
        return BookRepository.find_all()
    
    @staticmethod
    def get_available_books() -> List[Book]:
        """Get all available books"""
        return BookRepository.find_available()
    
    @staticmethod
    def get_book_by_id(book_id: str) -> Optional[Book]:
        """Get book by ID"""
        return BookRepository.find_by_id(book_id)
    
    @staticmethod
    def search_books(search_term: str) -> List[Book]:
        """Search books"""
        if not search_term:
            return BookRepository.find_all()
        return BookRepository.search(search_term)
    
    @staticmethod
    def create_book(book_data: dict) -> tuple[bool, str]:
        """
        Create a new book
        Returns: (success: bool, message: str)
        """
        # Validate required fields
        if not book_data.get('id'):
            return False, "Book ID is required"
        if not book_data.get('title'):
            return False, "Book title is required"
        
        # Check if book already exists
        existing = BookRepository.find_by_id(book_data['id'])
        if existing:
            return False, "Book with this ID already exists"
        
        # Set default values
        if 'total_copies' not in book_data:
            book_data['total_copies'] = 1
        if 'available_copies' not in book_data:
            book_data['available_copies'] = book_data['total_copies']
        
        # Create book
        book = Book.from_dict(book_data)
        success = BookRepository.create(book)
        
        if success:
            return True, "Book created successfully"
        return False, "Failed to create book"
    
    @staticmethod
    def update_book(book_data: dict) -> tuple[bool, str]:
        """
        Update book
        Returns: (success: bool, message: str)
        """
        book_id = book_data.get('id')
        if not book_id:
            return False, "Book ID is required"
        
        # Check if book exists
        existing = BookRepository.find_by_id(book_id)
        if not existing:
            return False, "Book not found"
        
        # Update book
        book = Book.from_dict(book_data)
        success = BookRepository.update(book)
        
        if success:
            return True, "Book updated successfully"
        return False, "Failed to update book"
    
    @staticmethod
    def delete_book(book_id: str) -> tuple[bool, str]:
        """
        Delete book
        Returns: (success: bool, message: str)
        """
        # Check if book exists
        existing = BookRepository.find_by_id(book_id)
        if not existing:
            return False, "Book not found"
        
        # TODO: Check if book has active issues
        
        success = BookRepository.delete(book_id)
        
        if success:
            return True, "Book deleted successfully"
        return False, "Failed to delete book"


