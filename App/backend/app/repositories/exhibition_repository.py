"""
Exhibition Repository - Data access layer for exhibitions
"""
from typing import List, Optional
from datetime import date
from app.database import get_db_connection
from app.models.exhibition import Exhibition
from app.models.book import Book
from psycopg2.extras import RealDictCursor


class ExhibitionRepository:
    """Repository for exhibition data access"""
    
    @staticmethod
    def find_all() -> List[Exhibition]:
        """Get all exhibitions"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT * FROM exhibitions 
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            return [Exhibition.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_active() -> List[Exhibition]:
        """Get all active exhibitions (based on is_active flag and dates)"""
        today = date.today()
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT * FROM exhibitions 
                WHERE is_active = TRUE
                AND (start_date IS NULL OR start_date <= %s)
                AND (end_date IS NULL OR end_date >= %s)
                ORDER BY created_at DESC
            ''', (today, today))
            rows = cursor.fetchall()
            return [Exhibition.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(exhibition_id: int) -> Optional[Exhibition]:
        """Find exhibition by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM exhibitions WHERE id = %s', (exhibition_id,))
            row = cursor.fetchone()
            return Exhibition.from_dict(dict(row)) if row else None
    
    @staticmethod
    def create(exhibition: Exhibition) -> Optional[int]:
        """Create a new exhibition and return its ID"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO exhibitions (title, description, start_date, end_date, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    exhibition.title,
                    exhibition.description,
                    exhibition.start_date.isoformat() if exhibition.start_date else None,
                    exhibition.end_date.isoformat() if exhibition.end_date else None,
                    exhibition.is_active
                ))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error creating exhibition: {e}")
            return None
    
    @staticmethod
    def update(exhibition: Exhibition) -> bool:
        """Update exhibition"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE exhibitions
                    SET title=%s, description=%s, start_date=%s, end_date=%s, is_active=%s
                    WHERE id=%s
                ''', (
                    exhibition.title,
                    exhibition.description,
                    exhibition.start_date.isoformat() if exhibition.start_date else None,
                    exhibition.end_date.isoformat() if exhibition.end_date else None,
                    exhibition.is_active,
                    exhibition.id
                ))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating exhibition: {e}")
            return False
    
    @staticmethod
    def delete(exhibition_id: int) -> bool:
        """Delete exhibition (cascade will delete exhibition_books)"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM exhibitions WHERE id = %s', (exhibition_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting exhibition: {e}")
            return False
    
    @staticmethod
    def add_book(exhibition_id: int, book_id: str, display_order: int = 0) -> bool:
        """Add a book to an exhibition"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                # Get max order if not specified
                if display_order == 0:
                    cursor.execute('''
                        SELECT COALESCE(MAX(display_order), 0) as max_order FROM exhibition_books 
                        WHERE exhibition_id = %s
                    ''', (exhibition_id,))
                    result = cursor.fetchone()
                    max_order = result['max_order'] if result and result['max_order'] else 0
                    display_order = max_order + 1
                
                cursor.execute('''
                    INSERT INTO exhibition_books (exhibition_id, book_id, display_order)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (exhibition_id, book_id) 
                    DO UPDATE SET display_order = EXCLUDED.display_order
                ''', (exhibition_id, book_id, display_order))
                return True
        except Exception as e:
            print(f"Error adding book to exhibition: {e}")
            return False
    
    @staticmethod
    def remove_book(exhibition_id: int, book_id: str) -> bool:
        """Remove a book from an exhibition"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM exhibition_books 
                    WHERE exhibition_id = %s AND book_id = %s
                ''', (exhibition_id, book_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing book from exhibition: {e}")
            return False
    
    @staticmethod
    def get_books(exhibition_id: int) -> List[Book]:
        """Get all books in an exhibition, ordered by display_order"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT b.* FROM books b
                INNER JOIN exhibition_books eb ON b.id = eb.book_id
                WHERE eb.exhibition_id = %s
                ORDER BY eb.display_order ASC
            ''', (exhibition_id,))
            rows = cursor.fetchall()
            return [Book.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def update_book_order(exhibition_id: int, book_orders: List[dict]) -> bool:
        """Update display order of books in an exhibition
        book_orders: [{'book_id': 'B0001', 'display_order': 1}, ...]
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                for item in book_orders:
                    cursor.execute('''
                        UPDATE exhibition_books
                        SET display_order = %s
                        WHERE exhibition_id = %s AND book_id = %s
                    ''', (item['display_order'], exhibition_id, item['book_id']))
                return True
        except Exception as e:
            print(f"Error updating book order: {e}")
            return False
    
    @staticmethod
    def remove_books_from_exhibitions(book_id: str) -> bool:
        """Remove a book from all exhibitions (called when book is deleted)"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM exhibition_books WHERE book_id = %s', (book_id,))
                return True
        except Exception as e:
            print(f"Error removing book from exhibitions: {e}")
            return False

