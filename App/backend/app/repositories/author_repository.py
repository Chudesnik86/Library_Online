"""
Author Repository - Data access layer for authors
"""
from typing import List, Optional
from app.database import get_db_connection
from app.models.author import Author
from psycopg2.extras import RealDictCursor


class AuthorRepository:
    """Repository for author operations"""
    
    @staticmethod
    def find_all() -> List[Author]:
        """Get all authors"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM authors ORDER BY full_name')
            rows = cursor.fetchall()
            return [Author.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(author_id: int) -> Optional[Author]:
        """Get author by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM authors WHERE id = %s', (author_id,))
            row = cursor.fetchone()
            return Author.from_dict(dict(row)) if row else None
    
    @staticmethod
    def search(search_term: str) -> List[Author]:
        """Search authors by name"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            search_pattern = f'%{search_term}%'
            cursor.execute('''
                SELECT * FROM authors
                WHERE full_name ILIKE %s
                ORDER BY full_name
            ''', (search_pattern,))
            rows = cursor.fetchall()
            return [Author.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def create(author: Author) -> bool:
        """Create a new author"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO authors (full_name, birth_date, death_date, biography, wikipedia_url)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    author.full_name,
                    author.birth_date,
                    author.death_date,
                    author.biography,
                    author.wikipedia_url
                ))
                result = cursor.fetchone()
                if result:
                    author.id = result[0]
                return True
        except Exception as e:
            print(f"Error creating author: {e}")
            return False
    
    @staticmethod
    def update(author: Author) -> bool:
        """Update author"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE authors
                    SET full_name = %s, birth_date = %s, death_date = %s,
                        biography = %s, wikipedia_url = %s
                    WHERE id = %s
                ''', (
                    author.full_name,
                    author.birth_date,
                    author.death_date,
                    author.biography,
                    author.wikipedia_url,
                    author.id
                ))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating author: {e}")
            return False
    
    @staticmethod
    def delete(author_id: int) -> bool:
        """Delete author"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM authors WHERE id = %s', (author_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting author: {e}")
            return False
    
    @staticmethod
    def get_by_book_id(book_id: str) -> List[Author]:
        """Get all authors for a book"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT a.* FROM authors a
                INNER JOIN book_authors ba ON a.id = ba.author_id
                WHERE ba.book_id = %s
                ORDER BY a.full_name
            ''', (book_id,))
            rows = cursor.fetchall()
            return [Author.from_dict(dict(row)) for row in rows]


