"""
Book Repository - Data access layer for books
"""
from typing import List, Optional
from app.database import get_db_connection
from app.models import Book
from psycopg2.extras import RealDictCursor


class BookRepository:
    """Repository for book data access"""
    
    @staticmethod
    def find_all() -> List[Book]:
        """Get all books"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM books ORDER BY title')
            rows = cursor.fetchall()
            return [Book.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_available() -> List[Book]:
        """Get all available books"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM books WHERE available_copies > 0 ORDER BY title')
            rows = cursor.fetchall()
            return [Book.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(book_id: str) -> Optional[Book]:
        """Find book by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
            row = cursor.fetchone()
            return Book.from_dict(dict(row)) if row else None
    
    @staticmethod
    def search(search_term: str) -> List[Book]:
        """Search books by ID, title, or author"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = '''
                SELECT * FROM books
                WHERE id LIKE %s OR title LIKE %s OR author LIKE %s
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
                    INSERT INTO books (id, title, author, isbn, category, total_copies, available_copies, description, cover_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    book.id,
                    book.title,
                    book.author,
                    book.isbn,
                    book.category,
                    book.total_copies,
                    book.available_copies,
                    book.description,
                    book.cover_image
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
                    SET title=%s, author=%s, isbn=%s, category=%s, total_copies=%s, available_copies=%s, description=%s, cover_image=%s
                    WHERE id=%s
                ''', (
                    book.title,
                    book.author,
                    book.isbn,
                    book.category,
                    book.total_copies,
                    book.available_copies,
                    book.description,
                    book.cover_image,
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
                cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
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
                    WHERE id = %s AND available_copies > 0
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
                    WHERE id = %s
                ''', (book_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error increasing available copies: {e}")
            return False
    
    @staticmethod
    def get_all_categories() -> List[str]:
        """Get all unique book categories"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT category 
                FROM books 
                WHERE category IS NOT NULL AND category != ''
                ORDER BY category
            ''')
            rows = cursor.fetchall()
            return [row[0] for row in rows if row[0]]
    
    @staticmethod
    def generate_unique_id() -> str:
        """Generate a unique book ID in format B####"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Get all book IDs that start with 'B'
            cursor.execute("SELECT id FROM books WHERE id LIKE %s", ('B%',))
            rows = cursor.fetchall()
            
            if rows:
                # Extract numbers from existing IDs and find the maximum
                max_num = 0
                for row in rows:
                    existing_id = row[0]
                    try:
                        # Extract number part (skip 'B' prefix)
                        num = int(existing_id[1:])
                        if num > max_num:
                            max_num = num
                    except ValueError:
                        continue
                new_num = max_num + 1
            else:
                new_num = 1
            
            # Format as B#### (4 digits)
            new_id = f"B{new_num:04d}"
            
            # Ensure uniqueness (in case of gaps or conflicts)
            while BookRepository.find_by_id(new_id):
                new_num += 1
                new_id = f"B{new_num:04d}"
            
            return new_id


