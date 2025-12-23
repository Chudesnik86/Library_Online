"""
Theme Repository - Data access layer for themes
Themes are stored directly in book_themes table as theme_name
"""
from typing import List, Optional
from app.database import get_db_connection
from app.models.theme import Theme
from psycopg2.extras import RealDictCursor


class ThemeRepository:
    """Repository for theme operations"""
    
    @staticmethod
    def find_all() -> List[Theme]:
        """Get all unique themes"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT DISTINCT theme_name as name FROM book_themes ORDER BY theme_name')
            rows = cursor.fetchall()
            themes = []
            for idx, row in enumerate(rows, start=1):
                theme_data = {'id': idx, 'name': row['name']}
                themes.append(Theme.from_dict(theme_data))
            return themes
    
    @staticmethod
    def find_by_name(name: str) -> Optional[Theme]:
        """Get theme by name"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT DISTINCT theme_name as name FROM book_themes WHERE theme_name = %s', (name,))
            row = cursor.fetchone()
            if row:
                theme_data = {'id': None, 'name': row['name']}
                return Theme.from_dict(theme_data)
            return None
    
    @staticmethod
    def get_by_book_id(book_id: str) -> List[Theme]:
        """Get all themes for a book"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT DISTINCT theme_name as name 
                FROM book_themes 
                WHERE book_id = %s 
                ORDER BY theme_name
            ''', (book_id,))
            rows = cursor.fetchall()
            themes = []
            for idx, row in enumerate(rows, start=1):
                theme_data = {'id': idx, 'name': row['name']}
                themes.append(Theme.from_dict(theme_data))
            return themes

