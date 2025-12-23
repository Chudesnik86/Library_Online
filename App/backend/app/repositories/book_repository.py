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
    def _get_authors_for_book(book_id: str) -> List[str]:
        """Get author names for a book (legacy method for backward compatibility)"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT a.full_name
                FROM authors a
                INNER JOIN book_authors ba ON a.id = ba.author_id
                WHERE ba.book_id = %s
                ORDER BY a.full_name
            ''', (book_id,))
            rows = cursor.fetchall()
            return [row['full_name'] for row in rows]
    
    @staticmethod
    def _get_authors_info_for_book(book_id: str) -> List[dict]:
        """Get full author information for a book including wikipedia_url, biography, dates"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT a.id, a.full_name, a.wikipedia_url, a.biography, a.birth_date, a.death_date
                FROM authors a
                INNER JOIN book_authors ba ON a.id = ba.author_id
                WHERE ba.book_id = %s
                ORDER BY a.full_name
            ''', (book_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def _get_covers_for_book(book_id: str) -> List[dict]:
        """Get all covers for a book"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT id, book_id, file_name
                FROM book_covers
                WHERE book_id = %s
                ORDER BY id
            ''', (book_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def find_all(page: int = None, per_page: int = None) -> tuple[List[Book], int]:
        """
        Get all books with optional pagination
        Returns: (books: List[Book], total_count: int)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get total count
            cursor.execute('SELECT COUNT(*) as count FROM books')
            total_count = cursor.fetchone()['count']
            
            # Build query with pagination
            if page is not None and per_page is not None:
                offset = (page - 1) * per_page
                cursor.execute('SELECT * FROM books ORDER BY title LIMIT %s OFFSET %s', (per_page, offset))
            else:
                cursor.execute('SELECT * FROM books ORDER BY title')
            
            rows = cursor.fetchall()
            books = []
            for row in rows:
                book_dict = dict(row)
                # Get authors info from book_authors table
                authors_info = BookRepository._get_authors_info_for_book(book_dict['id'])
                if authors_info:
                    book_dict['authors_info'] = authors_info
                    book_dict['author_names'] = [a['full_name'] for a in authors_info]
                else:
                    # If no authors in new table, use legacy author field
                    if book_dict.get('author'):
                        book_dict['author_names'] = [book_dict['author']]
                        book_dict['authors_info'] = [{'full_name': book_dict['author'], 'wikipedia_url': None}]
                    else:
                        book_dict['author_names'] = []
                        book_dict['authors_info'] = []
                
                # Get covers from book_covers table
                covers = BookRepository._get_covers_for_book(book_dict['id'])
                if covers:
                    book_dict['covers'] = covers
                else:
                    # If no covers in new table, use legacy cover_image field
                    if book_dict.get('cover_image'):
                        book_dict['covers'] = [{'id': None, 'book_id': book_dict['id'], 'file_name': book_dict['cover_image']}]
                    else:
                        book_dict['covers'] = []
                
                # Get categories/themes from book_themes table
                category = BookRepository._get_category_for_book(book_dict['id'])
                if category:
                    book_dict['category'] = category
                
                books.append(Book.from_dict(book_dict))
            return books, total_count
    
    @staticmethod
    def find_available(page: int = None, per_page: int = None) -> tuple[List[Book], int]:
        """
        Get all available books with optional pagination
        Returns: (books: List[Book], total_count: int)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get total count
            cursor.execute('SELECT COUNT(*) as count FROM books WHERE available_copies > 0')
            total_count = cursor.fetchone()['count']
            
            # Build query with pagination
            if page is not None and per_page is not None:
                offset = (page - 1) * per_page
                cursor.execute('SELECT * FROM books WHERE available_copies > 0 ORDER BY title LIMIT %s OFFSET %s', (per_page, offset))
            else:
                cursor.execute('SELECT * FROM books WHERE available_copies > 0 ORDER BY title')
            
            rows = cursor.fetchall()
            books = []
            for row in rows:
                book_dict = dict(row)
                # Get authors info from book_authors table
                authors_info = BookRepository._get_authors_info_for_book(book_dict['id'])
                if authors_info:
                    book_dict['authors_info'] = authors_info
                    book_dict['author_names'] = [a['full_name'] for a in authors_info]
                else:
                    # If no authors in new table, use legacy author field
                    if book_dict.get('author'):
                        book_dict['author_names'] = [book_dict['author']]
                        book_dict['authors_info'] = [{'full_name': book_dict['author'], 'wikipedia_url': None}]
                    else:
                        book_dict['author_names'] = []
                        book_dict['authors_info'] = []
                
                # Get covers from book_covers table
                covers = BookRepository._get_covers_for_book(book_dict['id'])
                if covers:
                    book_dict['covers'] = covers
                else:
                    # If no covers in new table, use legacy cover_image field
                    if book_dict.get('cover_image'):
                        book_dict['covers'] = [{'id': None, 'book_id': book_dict['id'], 'file_name': book_dict['cover_image']}]
                    else:
                        book_dict['covers'] = []
                
                # Get categories/themes from book_themes table
                category = BookRepository._get_category_for_book(book_dict['id'])
                if category:
                    book_dict['category'] = category
                
                books.append(Book.from_dict(book_dict))
            return books, total_count
    
    @staticmethod
    def find_by_id(book_id: str) -> Optional[Book]:
        """Find book by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
            row = cursor.fetchone()
            if not row:
                return None
            book_dict = dict(row)
            # Get authors info from book_authors table
            authors_info = BookRepository._get_authors_info_for_book(book_id)
            if authors_info:
                book_dict['authors_info'] = authors_info
                book_dict['author_names'] = [a['full_name'] for a in authors_info]
            else:
                # If no authors in new table, use legacy author field
                if book_dict.get('author'):
                    book_dict['author_names'] = [book_dict['author']]
                    book_dict['authors_info'] = [{'full_name': book_dict['author'], 'wikipedia_url': None}]
                else:
                    book_dict['author_names'] = []
                    book_dict['authors_info'] = []
            
            # Get covers from book_covers table
            covers = BookRepository._get_covers_for_book(book_id)
            if covers:
                book_dict['covers'] = covers
            else:
                # If no covers in new table, use legacy cover_image field
                if book_dict.get('cover_image'):
                    book_dict['covers'] = [{'id': None, 'book_id': book_id, 'file_name': book_dict['cover_image']}]
                else:
                    book_dict['covers'] = []
            
            # Get categories/themes from book_themes table
            category = BookRepository._get_category_for_book(book_id)
            if category:
                book_dict['category'] = category
            # If no themes, keep legacy category field or empty
            
            return Book.from_dict(book_dict)
    
    @staticmethod
    def search(search_term: str) -> List[Book]:
        """Search books by ID, title, or author (case-insensitive)"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = '''
                SELECT * FROM books
                WHERE id ILIKE %s OR title ILIKE %s OR author ILIKE %s
                ORDER BY title
            '''
            pattern = f'%{search_term}%'
            cursor.execute(query, (pattern, pattern, pattern))
            rows = cursor.fetchall()
            books = []
            for row in rows:
                book_dict = dict(row)
                # Get authors info from book_authors table
                authors_info = BookRepository._get_authors_info_for_book(book_dict['id'])
                if authors_info:
                    book_dict['authors_info'] = authors_info
                    book_dict['author_names'] = [a['full_name'] for a in authors_info]
                else:
                    # If no authors in new table, use legacy author field
                    if book_dict.get('author'):
                        book_dict['author_names'] = [book_dict['author']]
                        book_dict['authors_info'] = [{'full_name': book_dict['author'], 'wikipedia_url': None}]
                    else:
                        book_dict['author_names'] = []
                        book_dict['authors_info'] = []
                
                # Get covers from book_covers table
                covers = BookRepository._get_covers_for_book(book_dict['id'])
                if covers:
                    book_dict['covers'] = covers
                else:
                    # If no covers in new table, use legacy cover_image field
                    if book_dict.get('cover_image'):
                        book_dict['covers'] = [{'id': None, 'book_id': book_dict['id'], 'file_name': book_dict['cover_image']}]
                    else:
                        book_dict['covers'] = []
                
                # Get categories/themes from book_themes table
                category = BookRepository._get_category_for_book(book_dict['id'])
                if category:
                    book_dict['category'] = category
                
                books.append(Book.from_dict(book_dict))
            return books
    
    @staticmethod
    def advanced_search(title: str = None, author: str = None, theme: str = None) -> List[Book]:
        """Advanced search by title, author, and/or theme"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            conditions = []
            params = []
            
            if title:
                conditions.append("(books.title ILIKE %s OR books.subtitle ILIKE %s)")
                pattern = f'%{title}%'
                params.extend([pattern, pattern])
            
            if author:
                # Search in legacy author field and in book_authors table (case-insensitive)
                conditions.append("""
                    (books.author ILIKE %s OR EXISTS (
                        SELECT 1 FROM book_authors ba
                        JOIN authors a ON ba.author_id = a.id
                        WHERE ba.book_id = books.id AND a.full_name ILIKE %s
                    ))
                """)
                pattern = f'%{author}%'
                params.extend([pattern, pattern])
            
            if theme:
                # Search in legacy category field and in book_themes table (case-insensitive)
                conditions.append("""
                    (books.category ILIKE %s OR EXISTS (
                        SELECT 1 FROM book_themes bt
                        WHERE bt.book_id = books.id AND bt.theme_name ILIKE %s
                    ))
                """)
                pattern = f'%{theme}%'
                params.extend([pattern, pattern])
            
            if not conditions:
                # No search criteria, return all books
                query = 'SELECT * FROM books ORDER BY title'
                cursor.execute(query)
            else:
                query = f'SELECT DISTINCT books.* FROM books WHERE {" AND ".join(conditions)} ORDER BY title'
                cursor.execute(query, params)
            
            rows = cursor.fetchall()
            books = []
            for row in rows:
                book_dict = dict(row)
                # Get authors info from book_authors table
                authors_info = BookRepository._get_authors_info_for_book(book_dict['id'])
                if authors_info:
                    book_dict['authors_info'] = authors_info
                    book_dict['author_names'] = [a['full_name'] for a in authors_info]
                else:
                    # If no authors in new table, use legacy author field
                    if book_dict.get('author'):
                        book_dict['author_names'] = [book_dict['author']]
                        book_dict['authors_info'] = [{'full_name': book_dict['author'], 'wikipedia_url': None}]
                    else:
                        book_dict['author_names'] = []
                        book_dict['authors_info'] = []
                
                # Get covers from book_covers table
                covers = BookRepository._get_covers_for_book(book_dict['id'])
                if covers:
                    book_dict['covers'] = covers
                else:
                    # If no covers in new table, use legacy cover_image field
                    if book_dict.get('cover_image'):
                        book_dict['covers'] = [{'id': None, 'book_id': book_dict['id'], 'file_name': book_dict['cover_image']}]
                    else:
                        book_dict['covers'] = []
                
                # Get categories/themes from book_themes table
                category = BookRepository._get_category_for_book(book_dict['id'])
                if category:
                    book_dict['category'] = category
                
                books.append(Book.from_dict(book_dict))
            return books
    
    @staticmethod
    def create(book: Book) -> bool:
        """Create a new book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO books (id, title, subtitle, description, publication_year, isbn, 
                                      total_copies, available_copies, author, category, cover_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    book.id,
                    book.title,
                    book.subtitle,
                    book.description,
                    book.publication_year,
                    book.isbn,
                    book.total_copies,
                    book.available_copies,
                    book.author,  # Legacy field
                    book.category,  # Legacy field
                    book.cover_image  # Legacy field
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
                    SET title=%s, subtitle=%s, description=%s, publication_year=%s, isbn=%s, 
                        total_copies=%s, available_copies=%s, author=%s, category=%s, cover_image=%s
                    WHERE id=%s
                ''', (
                    book.title,
                    book.subtitle,
                    book.description,
                    book.publication_year,
                    book.isbn,
                    book.total_copies,
                    book.available_copies,
                    book.author,  # Legacy field
                    book.category,  # Legacy field
                    book.cover_image,  # Legacy field
                    book.id
                ))
                return True
        except Exception as e:
            print(f"Error updating book: {e}")
            return False
    
    @staticmethod
    def delete(book_id: str) -> bool:
        """
        Delete book
        All related records will be automatically deleted via CASCADE:
        - book_covers
        - book_themes  
        - book_authors
        - exhibition_books
        - issues
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting book: {e}")
            raise  # Re-raise to handle in service layer
    
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
    def _get_category_for_book(book_id: str) -> Optional[str]:
        """Get first category/theme for a book (for backward compatibility)"""
        from app.repositories import ThemeRepository
        themes = ThemeRepository.get_by_book_id(book_id)
        if themes and len(themes) > 0:
            return themes[0].name
        return None
    
    @staticmethod
    def get_all_categories() -> List[str]:
        """Get all unique book categories from book_themes table"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT theme_name 
                FROM book_themes 
                WHERE theme_name IS NOT NULL AND theme_name != ''
                ORDER BY theme_name
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
    
    @staticmethod
    def add_theme(book_id: str, theme_name: str) -> bool:
        """Add theme to book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO book_themes (book_id, theme_name)
                    VALUES (%s, %s)
                    ON CONFLICT (book_id, theme_name) DO NOTHING
                ''', (book_id, theme_name))
                return True
        except Exception as e:
            print(f"Error adding theme to book: {e}")
            return False
    
    @staticmethod
    def remove_theme(book_id: str, theme_name: str) -> bool:
        """Remove theme from book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM book_themes WHERE book_id = %s AND theme_name = %s', (book_id, theme_name))
                return True
        except Exception as e:
            print(f"Error removing theme from book: {e}")
            return False
    
    @staticmethod
    def set_themes(book_id: str, theme_names: List[str]) -> bool:
        """Set themes for a book (replaces existing)"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Remove existing themes
                cursor.execute('DELETE FROM book_themes WHERE book_id = %s', (book_id,))
                # Add new themes
                for theme_name in theme_names:
                    cursor.execute('''
                        INSERT INTO book_themes (book_id, theme_name)
                        VALUES (%s, %s)
                    ''', (book_id, theme_name))
                return True
        except Exception as e:
            print(f"Error setting themes for book: {e}")
            return False
    
    @staticmethod
    def add_author(book_id: str, author_id: int) -> bool:
        """Add author to book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO book_authors (book_id, author_id)
                    VALUES (%s, %s)
                    ON CONFLICT (book_id, author_id) DO NOTHING
                ''', (book_id, author_id))
                return True
        except Exception as e:
            print(f"Error adding author to book: {e}")
            return False
    
    @staticmethod
    def remove_author(book_id: str, author_id: int) -> bool:
        """Remove author from book"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM book_authors WHERE book_id = %s AND author_id = %s', (book_id, author_id))
                return True
        except Exception as e:
            print(f"Error removing author from book: {e}")
            return False
    
    @staticmethod
    def set_authors(book_id: str, author_ids: List[int]) -> bool:
        """Set authors for a book (replaces existing)"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Remove existing authors
                cursor.execute('DELETE FROM book_authors WHERE book_id = %s', (book_id,))
                # Add new authors
                for author_id in author_ids:
                    cursor.execute('''
                        INSERT INTO book_authors (book_id, author_id)
                        VALUES (%s, %s)
                    ''', (book_id, author_id))
                return True
        except Exception as e:
            print(f"Error setting authors for book: {e}")
            return False


