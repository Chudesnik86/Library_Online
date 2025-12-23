"""
Book Cover Repository - Data access layer for book covers
"""
from typing import List, Optional
from app.database import get_db_connection
from app.models.book_cover import BookCover
from psycopg2.extras import RealDictCursor


class BookCoverRepository:
    """Repository for book cover operations"""
    
    @staticmethod
    def find_by_book_id(book_id: str) -> List[BookCover]:
        """Get all covers for a book"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM book_covers WHERE book_id = %s ORDER BY id', (book_id,))
            rows = cursor.fetchall()
            return [BookCover.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(cover_id: int) -> Optional[BookCover]:
        """Get cover by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM book_covers WHERE id = %s', (cover_id,))
            row = cursor.fetchone()
            return BookCover.from_dict(dict(row)) if row else None
    
    @staticmethod
    def create(cover: BookCover) -> bool:
        """Create a new book cover"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO book_covers (book_id, file_name)
                    VALUES (%s, %s)
                    RETURNING id
                ''', (cover.book_id, cover.file_name))
                result = cursor.fetchone()
                if result:
                    cover.id = result[0]
                return True
        except Exception as e:
            print(f"Error creating book cover: {e}")
            return False
    
    @staticmethod
    def delete(cover_id: int) -> bool:
        """Delete book cover"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM book_covers WHERE id = %s', (cover_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting book cover: {e}")
            return False
    
    @staticmethod
    def delete_by_book_id(book_id: str) -> bool:
        """Delete all covers for a book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM book_covers WHERE book_id = %s', (book_id,))
                return True
        except Exception as e:
            print(f"Error deleting book covers: {e}")
            return False


