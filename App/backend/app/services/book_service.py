"""
Book Service - Business logic for book operations
"""
from typing import List, Optional
from app.models import Book
from app.repositories import BookRepository


class BookService:
    """Service for book business logic"""
    
    @staticmethod
    def get_all_books(page: int = None, per_page: int = None) -> tuple[List[Book], int]:
        """
        Get all books with optional pagination
        Returns: (books: List[Book], total_count: int)
        """
        return BookRepository.find_all(page, per_page)
    
    @staticmethod
    def get_available_books(page: int = None, per_page: int = None) -> tuple[List[Book], int]:
        """
        Get all available books with optional pagination
        Returns: (books: List[Book], total_count: int)
        """
        return BookRepository.find_available(page, per_page)
    
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
    def advanced_search_books(title: str = None, author: str = None, theme: str = None) -> List[Book]:
        """Advanced search books by title, author, and/or theme"""
        return BookRepository.advanced_search(title, author, theme)
    
    @staticmethod
    def create_book(book_data: dict) -> tuple[bool, str]:
        """
        Create a new book
        Returns: (success: bool, message: str)
        """
        # Validate required fields
        if not book_data.get('title'):
            return False, "Book title is required"
        
        # Generate ID automatically if not provided
        if not book_data.get('id'):
            book_data['id'] = BookRepository.generate_unique_id()
        else:
            # Check if book already exists (only if ID was provided)
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
        
        if not success:
            return False, "Failed to create book"
        
        # Handle authors if provided
        authors_info = book_data.get('authors_info', [])
        author_names = book_data.get('author_names', [])
        
        if authors_info:
            # Use authors_info if provided (includes wikipedia_url)
            from app.repositories import AuthorRepository
            author_ids = []
            
            for author_info in authors_info:
                author_name = (author_info.get('name') or '').strip()
                wikipedia_url = author_info.get('wikipedia_url')
                if wikipedia_url:
                    wikipedia_url = str(wikipedia_url).strip() or None
                else:
                    wikipedia_url = None
                
                if not author_name:
                    continue
                
                # Try to find existing author
                existing_authors = AuthorRepository.search(author_name)
                author = None
                
                # Find exact match
                for existing in existing_authors:
                    if existing.full_name.lower() == author_name.lower():
                        author = existing
                        break
                
                # If not found, create new author
                if not author:
                    from app.models.author import Author
                    new_author = Author(full_name=author_name, wikipedia_url=wikipedia_url)
                    if AuthorRepository.create(new_author):
                        author = AuthorRepository.find_by_id(new_author.id)
                else:
                    # Update existing author's wikipedia_url if provided
                    if wikipedia_url and author.wikipedia_url != wikipedia_url:
                        author.wikipedia_url = wikipedia_url
                        AuthorRepository.update(author)
                
                if author and author.id:
                    author_ids.append(author.id)
            
            # Set authors for the book
            if author_ids:
                BookRepository.set_authors(book_data['id'], author_ids)
        elif author_names:
            # Fallback to author_names if authors_info not provided
            from app.repositories import AuthorRepository
            author_ids = []
            
            for author_name in author_names:
                if not author_name or not author_name.strip():
                    continue
                
                author_name = author_name.strip()
                # Try to find existing author
                existing_authors = AuthorRepository.search(author_name)
                author = None
                
                # Find exact match
                for existing in existing_authors:
                    if existing.full_name.lower() == author_name.lower():
                        author = existing
                        break
                
                # If not found, create new author
                if not author:
                    from app.models.author import Author
                    new_author = Author(full_name=author_name)
                    if AuthorRepository.create(new_author):
                        author = AuthorRepository.find_by_id(new_author.id)
                
                if author and author.id:
                    author_ids.append(author.id)
            
            # Set authors for the book
            if author_ids:
                BookRepository.set_authors(book_data['id'], author_ids)
        
        # Handle categories/themes if provided
        category = book_data.get('category', '').strip()
        if category:
            # Save category to book_themes table
            BookRepository.set_themes(book_data['id'], [category])
        
        # Handle covers if provided
        covers = book_data.get('covers', [])
        if covers:
            from app.repositories import BookCoverRepository
            from app.models.book_cover import BookCover
            
            # Delete existing covers
            BookCoverRepository.delete_by_book_id(book_data['id'])
            
            # Create new covers
            for cover_data in covers:
                file_name = cover_data.get('file_name', '') if isinstance(cover_data, dict) else str(cover_data)
                if file_name:
                    cover = BookCover(book_id=book_data['id'], file_name=file_name)
                    BookCoverRepository.create(cover)
        
        return True, f"Book created successfully with ID: {book_data['id']}"
    
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
        
        if not success:
            return False, "Failed to update book"
        
        # Handle authors if provided
        authors_info = book_data.get('authors_info', [])
        author_names = book_data.get('author_names', [])
        
        if authors_info is not None:  # Explicitly provided (even if empty list)
            # Use authors_info if provided (includes wikipedia_url)
            from app.repositories import AuthorRepository
            author_ids = []
            
            for author_info in authors_info:
                author_name = (author_info.get('name') or '').strip()
                wikipedia_url = author_info.get('wikipedia_url')
                if wikipedia_url:
                    wikipedia_url = str(wikipedia_url).strip() or None
                else:
                    wikipedia_url = None
                
                if not author_name:
                    continue
                
                # Try to find existing author
                existing_authors = AuthorRepository.search(author_name)
                author = None
                
                # Find exact match
                for existing in existing_authors:
                    if existing.full_name.lower() == author_name.lower():
                        author = existing
                        break
                
                # If not found, create new author
                if not author:
                    from app.models.author import Author
                    new_author = Author(full_name=author_name, wikipedia_url=wikipedia_url)
                    if AuthorRepository.create(new_author):
                        author = AuthorRepository.find_by_id(new_author.id)
                else:
                    # Update existing author's wikipedia_url if provided
                    if wikipedia_url and author.wikipedia_url != wikipedia_url:
                        author.wikipedia_url = wikipedia_url
                        AuthorRepository.update(author)
                
                if author and author.id:
                    author_ids.append(author.id)
            
            # Set authors for the book (this will replace existing)
            if author_ids:
                BookRepository.set_authors(book_id, author_ids)
            else:
                # Remove all authors if empty list provided
                BookRepository.set_authors(book_id, [])
        elif author_names is not None:  # Fallback to author_names
            from app.repositories import AuthorRepository
            author_ids = []
            
            for author_name in author_names:
                if not author_name or not author_name.strip():
                    continue
                
                author_name = author_name.strip()
                # Try to find existing author
                existing_authors = AuthorRepository.search(author_name)
                author = None
                
                # Find exact match
                for existing in existing_authors:
                    if existing.full_name.lower() == author_name.lower():
                        author = existing
                        break
                
                # If not found, create new author
                if not author:
                    from app.models.author import Author
                    new_author = Author(full_name=author_name)
                    if AuthorRepository.create(new_author):
                        author = AuthorRepository.find_by_id(new_author.id)
                
                if author and author.id:
                    author_ids.append(author.id)
            
            # Set authors for the book (this will replace existing)
            if author_ids:
                BookRepository.set_authors(book_id, author_ids)
            else:
                # Remove all authors if empty list provided
                BookRepository.set_authors(book_id, [])
        
        # Handle categories/themes if provided
        category = book_data.get('category', '').strip()
        if category:
            # Save category to book_themes table (replaces existing)
            BookRepository.set_themes(book_id, [category])
        else:
            # Remove all categories if empty
            BookRepository.set_themes(book_id, [])
        
        # Handle covers if provided
        covers = book_data.get('covers', [])
        if covers is not None:  # Explicitly provided (even if empty list)
            from app.repositories import BookCoverRepository
            from app.models.book_cover import BookCover
            
            # Delete existing covers
            BookCoverRepository.delete_by_book_id(book_id)
            
            # Create new covers
            for cover_data in covers:
                file_name = cover_data.get('file_name', '') if isinstance(cover_data, dict) else str(cover_data)
                if file_name:
                    cover = BookCover(book_id=book_id, file_name=file_name)
                    BookCoverRepository.create(cover)
        
        return True, "Book updated successfully"
    
    @staticmethod
    def delete_book(book_id: str) -> tuple[bool, str]:
        """
        Delete book and all related data
        All related records will be automatically deleted via CASCADE:
        - book_covers
        - book_themes
        - book_authors
        - exhibition_books
        - issues (all issues for this book)
        Returns: (success: bool, message: str)
        """
        # Check if book exists
        existing = BookRepository.find_by_id(book_id)
        if not existing:
            return False, "Книга не найдена"
        
        # Delete book - all related data will be deleted automatically via CASCADE
        try:
            success = BookRepository.delete(book_id)
            if success:
                return True, "Книга успешно удалена"
            return False, "Не удалось удалить книгу"
        except Exception as e:
            error_msg = str(e)
            # Check for foreign key constraint errors
            if 'foreign key' in error_msg.lower() or 'constraint' in error_msg.lower():
                return False, f"Не удалось удалить книгу: есть связанные записи. {error_msg}"
            return False, f"Ошибка при удалении книги: {error_msg}"


