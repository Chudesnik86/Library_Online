"""
Book Repository - Data access layer for books
"""
from typing import List, Optional
from app.database import get_db_connection
from app.models import Book


class BookRepository:
    """Repository for book data access"""
    
    @staticmethod
    def find_all() -> List[Book]:
        """Get all books"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books ORDER BY title')
            rows = cursor.fetchall()
            return [Book.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_available() -> List[Book]:
        """Get all available books"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books WHERE available_copies > 0 ORDER BY title')
            rows = cursor.fetchall()
            return [Book.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(book_id: str) -> Optional[Book]:
        """Find book by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            row = cursor.fetchone()
            return Book.from_dict(dict(row)) if row else None
    
    @staticmethod
    def search(search_term: str) -> List[Book]:
        """Search books by ID, title, or author"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM books
                WHERE id LIKE ? OR title LIKE ? OR author LIKE ?
                ORDER BY title
            '''
            pattern = f'%{search_term}%'
            cursor.execute(query, (pattern, pattern, pattern))
            rows = cursor.fetchall()
            return [Book.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def create(book: Book) -> bool:
        """Create a new book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO books (id, title, author, isbn, category, total_copies, available_copies)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    book.id,
                    book.title,
                    book.author,
                    book.isbn,
                    book.category,
                    book.total_copies,
                    book.available_copies
                ))
                return True
        except Exception as e:
            print(f"Error creating book: {e}")
            return False
    
    @staticmethod
    def update(book: Book) -> bool:
        """Update book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE books
                    SET title=?, author=?, isbn=?, category=?, total_copies=?, available_copies=?
                    WHERE id=?
                ''', (
                    book.title,
                    book.author,
                    book.isbn,
                    book.category,
                    book.total_copies,
                    book.available_copies,
                    book.id
                ))
                return True
        except Exception as e:
            print(f"Error updating book: {e}")
            return False
    
    @staticmethod
    def delete(book_id: str) -> bool:
        """Delete book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
                return True
        except Exception as e:
            print(f"Error deleting book: {e}")
            return False
    
    @staticmethod
    def decrease_available_copies(book_id: str) -> bool:
        """Decrease available copies when book is borrowed"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE books
                    SET available_copies = available_copies - 1
                    WHERE id = ? AND available_copies > 0
                ''', (book_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error decreasing available copies: {e}")
            return False
    
    @staticmethod
    def increase_available_copies(book_id: str) -> bool:
        """Increase available copies when book is returned"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE books
                    SET available_copies = available_copies + 1
                    WHERE id = ?
                ''', (book_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error increasing available copies: {e}")
            return False


