"""
Exhibition Service - Business logic for exhibition operations
"""
from typing import List, Optional, Dict
from datetime import date
from app.models import Exhibition, Book
from app.repositories import ExhibitionRepository, BookRepository


class ExhibitionService:
    """Service for exhibition business logic"""
    
    @staticmethod
    def get_all_exhibitions() -> List[Exhibition]:
        """Get all exhibitions"""
        return ExhibitionRepository.find_all()
    
    @staticmethod
    def get_active_exhibitions() -> List[Exhibition]:
        """Get all currently active exhibitions"""
        return ExhibitionRepository.find_active()
    
    @staticmethod
    def get_exhibition_by_id(exhibition_id: int) -> Optional[Exhibition]:
        """Get exhibition by ID"""
        return ExhibitionRepository.find_by_id(exhibition_id)
    
    @staticmethod
    def get_exhibition_with_books(exhibition_id: int) -> Optional[Dict]:
        """Get exhibition with its books"""
        exhibition = ExhibitionRepository.find_by_id(exhibition_id)
        if not exhibition:
            return None
        
        books = ExhibitionRepository.get_books(exhibition_id)
        
        return {
            'exhibition': exhibition.to_dict(),
            'books': [book.to_dict() for book in books]
        }
    
    @staticmethod
    def create_exhibition(exhibition_data: dict) -> tuple[bool, str, Optional[int]]:
        """
        Create a new exhibition
        Returns: (success: bool, message: str, exhibition_id: Optional[int])
        """
        # Validate required fields
        if not exhibition_data.get('title'):
            return False, "Exhibition title is required", None
        
        # Validate dates
        start_date = None
        end_date = None
        
        if exhibition_data.get('start_date'):
            try:
                start_date = date.fromisoformat(exhibition_data['start_date'])
            except ValueError:
                return False, "Invalid start date format (use YYYY-MM-DD)", None
        
        if exhibition_data.get('end_date'):
            try:
                end_date = date.fromisoformat(exhibition_data['end_date'])
            except ValueError:
                return False, "Invalid end date format (use YYYY-MM-DD)", None
        
        if start_date and end_date and start_date > end_date:
            return False, "Start date cannot be after end date", None
        
        # Create exhibition
        exhibition = Exhibition(
            title=exhibition_data['title'],
            description=exhibition_data.get('description'),
            start_date=start_date,
            end_date=end_date,
            is_active=exhibition_data.get('is_active', True)
        )
        
        exhibition_id = ExhibitionRepository.create(exhibition)
        
        if exhibition_id:
            return True, "Exhibition created successfully", exhibition_id
        return False, "Failed to create exhibition", None
    
    @staticmethod
    def update_exhibition(exhibition_data: dict) -> tuple[bool, str]:
        """
        Update exhibition
        Returns: (success: bool, message: str)
        """
        exhibition_id = exhibition_data.get('id')
        if not exhibition_id:
            return False, "Exhibition ID is required"
        
        # Check if exhibition exists
        existing = ExhibitionRepository.find_by_id(exhibition_id)
        if not existing:
            return False, "Exhibition not found"
        
        # Validate dates
        start_date = None
        end_date = None
        
        if exhibition_data.get('start_date'):
            try:
                start_date = date.fromisoformat(exhibition_data['start_date'])
            except ValueError:
                return False, "Invalid start date format (use YYYY-MM-DD)"
        
        if exhibition_data.get('end_date'):
            try:
                end_date = date.fromisoformat(exhibition_data['end_date'])
            except ValueError:
                return False, "Invalid end date format (use YYYY-MM-DD)"
        
        if start_date and end_date and start_date > end_date:
            return False, "Start date cannot be after end date"
        
        # Update exhibition
        exhibition = Exhibition(
            id=exhibition_id,
            title=exhibition_data.get('title', existing.title),
            description=exhibition_data.get('description', existing.description),
            start_date=start_date if start_date else existing.start_date,
            end_date=end_date if end_date else existing.end_date,
            is_active=exhibition_data.get('is_active', existing.is_active)
        )
        
        success = ExhibitionRepository.update(exhibition)
        
        if success:
            return True, "Exhibition updated successfully"
        return False, "Failed to update exhibition"
    
    @staticmethod
    def delete_exhibition(exhibition_id: int) -> tuple[bool, str]:
        """
        Delete exhibition
        Returns: (success: bool, message: str)
        """
        # Check if exhibition exists
        existing = ExhibitionRepository.find_by_id(exhibition_id)
        if not existing:
            return False, "Exhibition not found"
        
        success = ExhibitionRepository.delete(exhibition_id)
        
        if success:
            return True, "Exhibition deleted successfully"
        return False, "Failed to delete exhibition"
    
    @staticmethod
    def add_book_to_exhibition(exhibition_id: int, book_id: str, display_order: int = 0) -> tuple[bool, str]:
        """
        Add a book to an exhibition
        Returns: (success: bool, message: str)
        """
        # Check if exhibition exists
        exhibition = ExhibitionRepository.find_by_id(exhibition_id)
        if not exhibition:
            return False, "Exhibition not found"
        
        # Check if book exists
        book = BookRepository.find_by_id(book_id)
        if not book:
            return False, "Book not found"
        
        # Check book limit (3-12 books per exhibition)
        books = ExhibitionRepository.get_books(exhibition_id)
        if len(books) >= 12:
            return False, "Exhibition cannot contain more than 12 books"
        
        success = ExhibitionRepository.add_book(exhibition_id, book_id, display_order)
        
        if success:
            return True, "Book added to exhibition successfully"
        return False, "Failed to add book to exhibition"
    
    @staticmethod
    def remove_book_from_exhibition(exhibition_id: int, book_id: str) -> tuple[bool, str]:
        """
        Remove a book from an exhibition
        Returns: (success: bool, message: str)
        """
        # Check minimum books (at least 3 books recommended)
        books = ExhibitionRepository.get_books(exhibition_id)
        if len(books) <= 1:
            return False, "Exhibition must contain at least one book"
        
        success = ExhibitionRepository.remove_book(exhibition_id, book_id)
        
        if success:
            return True, "Book removed from exhibition successfully"
        return False, "Failed to remove book from exhibition"
    
    @staticmethod
    def update_book_order(exhibition_id: int, book_orders: List[dict]) -> tuple[bool, str]:
        """
        Update display order of books in an exhibition
        Returns: (success: bool, message: str)
        """
        # Check if exhibition exists
        exhibition = ExhibitionRepository.find_by_id(exhibition_id)
        if not exhibition:
            return False, "Exhibition not found"
        
        success = ExhibitionRepository.update_book_order(exhibition_id, book_orders)
        
        if success:
            return True, "Book order updated successfully"
        return False, "Failed to update book order"
    
    @staticmethod
    def toggle_exhibition_status(exhibition_id: int) -> tuple[bool, str]:
        """
        Toggle exhibition active status
        Returns: (success: bool, message: str)
        """
        exhibition = ExhibitionRepository.find_by_id(exhibition_id)
        if not exhibition:
            return False, "Exhibition not found"
        
        exhibition.is_active = not exhibition.is_active
        success = ExhibitionRepository.update(exhibition)
        
        if success:
            status = "activated" if exhibition.is_active else "deactivated"
            return True, f"Exhibition {status} successfully"
        return False, "Failed to update exhibition status"

