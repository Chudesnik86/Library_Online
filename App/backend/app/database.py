"""
Database initialization and connection management
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.extras
import json
import os
from contextlib import contextmanager
from config import DATABASE_CONFIG, SAMPLE_DATA_DIR


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    conn.set_session(autocommit=False)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database schema"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tables without foreign keys first
        # Customers table (no dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address TEXT,
                zip INTEGER,
                city VARCHAR(255),
                phone VARCHAR(50),
                email VARCHAR(255)
            )
        ''')
        
        # Authors table (no dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                birth_date DATE,
                death_date DATE,
                biography TEXT,
                wikipedia_url TEXT
            )
        ''')
        
        # Books table (no dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                subtitle VARCHAR(500),
                description TEXT,
                publication_year INTEGER,
                isbn VARCHAR(50),
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                -- Legacy fields for backward compatibility
                author VARCHAR(255),
                category VARCHAR(255),
                cover_image TEXT
            )
        ''')
        
        # Migrate existing books table to add new columns if they don't exist
        # PostgreSQL doesn't support IF NOT EXISTS for ALTER TABLE, so we check first
        columns_to_add = [
            ('subtitle', 'VARCHAR(500)'),
            ('description', 'TEXT'),
            ('publication_year', 'INTEGER'),
            ('author', 'VARCHAR(255)'),
            ('category', 'VARCHAR(255)'),
            ('cover_image', 'TEXT')
        ]
        
        for col_name, col_type in columns_to_add:
            cursor.execute('''
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='books' AND column_name=%s
            ''', (col_name,))
            if not cursor.fetchone():
                cursor.execute(f'ALTER TABLE books ADD COLUMN {col_name} {col_type}')
        
        # Book covers table (depends on books)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_covers (
                id SERIAL PRIMARY KEY,
                book_id VARCHAR(50) NOT NULL,
                file_name VARCHAR(500) NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        ''')
        
        # Book-Themes relationship (theme name stored directly)
        # Check if old structure exists (with theme_id)
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='book_themes' AND column_name='theme_id'
        ''')
        old_structure_exists = cursor.fetchone()
        
        if old_structure_exists:
            # Migrate from old structure (theme_id) to new structure (theme_name)
            # First, get theme names from old themes table if it exists
            cursor.execute('''
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='themes'
            ''')
            themes_table_exists = cursor.fetchone()
            
            if themes_table_exists:
                # Migrate data: get theme names from themes table
                # Use RealDictCursor for this query to get dict results
                temp_cursor = conn.cursor(cursor_factory=RealDictCursor)
                temp_cursor.execute('''
                    SELECT bt.book_id, t.name as theme_name
                    FROM book_themes bt
                    INNER JOIN themes t ON bt.theme_id = t.id
                ''')
                theme_mappings = temp_cursor.fetchall()
                temp_cursor.close()
                
                # Drop old table
                cursor.execute('DROP TABLE IF EXISTS book_themes CASCADE')
                
                # Create new table
                cursor.execute('''
                    CREATE TABLE book_themes (
                        id SERIAL PRIMARY KEY,
                        book_id VARCHAR(50) NOT NULL,
                        theme_name VARCHAR(255) NOT NULL,
                        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                        UNIQUE(book_id, theme_name)
                    )
                ''')
                
                # Insert migrated data
                for mapping in theme_mappings:
                    cursor.execute('''
                        INSERT INTO book_themes (book_id, theme_name)
                        VALUES (%s, %s)
                        ON CONFLICT (book_id, theme_name) DO NOTHING
                    ''', (mapping['book_id'], mapping['theme_name']))
                
                # Drop old themes table
                cursor.execute('DROP TABLE IF EXISTS themes CASCADE')
            else:
                # Just drop and recreate with new structure
                cursor.execute('DROP TABLE IF EXISTS book_themes CASCADE')
                cursor.execute('''
                    CREATE TABLE book_themes (
                        id SERIAL PRIMARY KEY,
                        book_id VARCHAR(50) NOT NULL,
                        theme_name VARCHAR(255) NOT NULL,
                        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                        UNIQUE(book_id, theme_name)
                    )
                ''')
        else:
            # Create new table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS book_themes (
                    id SERIAL PRIMARY KEY,
                    book_id VARCHAR(50) NOT NULL,
                    theme_name VARCHAR(255) NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                    UNIQUE(book_id, theme_name)
                )
            ''')
        
        # Drop themes table if it still exists
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'themes'
            )
        ''')
        if cursor.fetchone()[0]:
            cursor.execute('DROP TABLE IF EXISTS themes CASCADE')
        
        # Book-Authors many-to-many relationship
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_authors (
                id SERIAL PRIMARY KEY,
                book_id VARCHAR(50) NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
                UNIQUE(book_id, author_id)
            )
        ''')
        
        # Exhibitions table (no dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exhibitions (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table (depends on customers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                customer_id VARCHAR(50),
                name VARCHAR(255)
            )
        ''')
        
        # Add foreign key constraint for users if it doesn't exist
        cursor.execute('''
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='users' 
            AND constraint_type='FOREIGN KEY'
            AND constraint_name LIKE '%customer_id%'
        ''')
        if not cursor.fetchone():
            cursor.execute('''
                ALTER TABLE users 
                ADD CONSTRAINT fk_users_customer_id 
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            ''')
        
        # Issues table (depends on books and customers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id SERIAL PRIMARY KEY,
                book_id VARCHAR(50) NOT NULL,
                book_title VARCHAR(500) NOT NULL,
                customer_id VARCHAR(50) NOT NULL,
                customer_name VARCHAR(255) NOT NULL,
                date_issued DATE NOT NULL,
                date_return DATE,
                status VARCHAR(50) DEFAULT 'issued',
                extended BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Add extended column if it doesn't exist (for existing databases)
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='issues' AND column_name='extended'
        ''')
        if not cursor.fetchone():
            cursor.execute('ALTER TABLE issues ADD COLUMN extended BOOLEAN DEFAULT FALSE')
        
        # Add foreign key constraints for issues if they don't exist
        # Always drop and recreate to ensure CASCADE is set
        cursor.execute('ALTER TABLE issues DROP CONSTRAINT IF EXISTS fk_issues_book_id')
        cursor.execute('''
            ALTER TABLE issues 
            ADD CONSTRAINT fk_issues_book_id 
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        ''')
        
        # Check if customer_id constraint exists
        cursor.execute('''
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='issues' 
            AND constraint_type='FOREIGN KEY'
            AND constraint_name LIKE '%customer_id%'
        ''')
        customer_fk_exists = cursor.fetchone()
        
        if customer_fk_exists:
            # Drop existing constraint to recreate with CASCADE
            cursor.execute('''
                ALTER TABLE issues 
                DROP CONSTRAINT IF EXISTS fk_issues_customer_id
            ''')
        
        # Add constraint with CASCADE to auto-delete issues when customer is deleted
        cursor.execute('''
            ALTER TABLE issues 
            ADD CONSTRAINT fk_issues_customer_id 
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        ''')
        
        # Exhibition books (many-to-many relationship, depends on exhibitions and books)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exhibition_books (
                id SERIAL PRIMARY KEY,
                exhibition_id INTEGER NOT NULL,
                book_id VARCHAR(50) NOT NULL,
                display_order INTEGER DEFAULT 0,
                FOREIGN KEY (exhibition_id) REFERENCES exhibitions(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                UNIQUE(exhibition_id, book_id)
            )
        ''')
        
        # Add foreign key constraints for exhibition_books if they don't exist
        cursor.execute('''
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='exhibition_books' 
            AND constraint_type='FOREIGN KEY'
            AND constraint_name LIKE '%exhibition_id%'
        ''')
        if not cursor.fetchone():
            cursor.execute('''
                ALTER TABLE exhibition_books 
                ADD CONSTRAINT fk_exhibition_books_exhibition_id 
                FOREIGN KEY (exhibition_id) REFERENCES exhibitions(id) ON DELETE CASCADE
            ''')
        
        cursor.execute('''
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='exhibition_books' 
            AND constraint_type='FOREIGN KEY'
            AND constraint_name LIKE '%book_id%'
        ''')
        if not cursor.fetchone():
            cursor.execute('''
                ALTER TABLE exhibition_books 
                ADD CONSTRAINT fk_exhibition_books_book_id 
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            ''')
        
        # Drop themes table if it exists (no longer needed)
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'themes'
            )
        ''')
        result = cursor.fetchone()
        if result and result[0]:
            print("Dropping old themes table...")
            cursor.execute('DROP TABLE IF EXISTS themes CASCADE')
            print("[OK] Old themes table dropped")
        
        conn.commit()


def create_default_admin():
    """Create default admin user if not exists"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if admin exists
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='admin'")
        result = cursor.fetchone()
        if result and result['count'] == 0:
            # Create default admin
            from app.models.user import User
            password_hash = User.hash_password('admin123')  # Default password
            cursor.execute('''
                INSERT INTO users (email, password_hash, role, name)
                VALUES (%s, %s, %s, %s)
            ''', ('admin@library.com', password_hash, 'admin', 'Администратор'))
            conn.commit()
            print("[OK] Default admin created: admin@library.com / admin123")


def import_sample_data():
    """Import sample data if database is empty"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) as count FROM customers')
        result = cursor.fetchone()
        if result and result['count'] > 0:
            return  # Data already imported
        
        # Import customers
        customers_file = os.path.join(SAMPLE_DATA_DIR, 'Customers.json')
        if os.path.exists(customers_file):
            with open(customers_file, 'r', encoding='utf-8') as f:
                customers = json.load(f)
                for customer in customers:
                    cursor.execute('''
                        INSERT INTO customers (id, name, address, zip, city, phone, email)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    ''', (
                        customer['ID'],
                        customer['Name'],
                        customer['Address'],
                        customer['Zip'],
                        customer['City'],
                        customer['Phone'],
                        customer['Email']
                    ))
        
        # Import issues and extract books
        issues_file = os.path.join(SAMPLE_DATA_DIR, 'Issues.json')
        if os.path.exists(issues_file):
            with open(issues_file, 'r', encoding='utf-8') as f:
                issues = json.load(f)

                # Extract unique books
                books_dict = {}
                for issue in issues:
                    book_id = issue['Book ID']
                    if book_id not in books_dict:
                        books_dict[book_id] = issue['Book']

                # Insert books
                for book_id, book_title in books_dict.items():
                    cursor.execute('''
                        INSERT INTO books (id, title, author, isbn, category, total_copies, available_copies)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    ''', (book_id, book_title, '', '', '', 1, 1))

                # Insert issues
                for issue in issues:
                    # Convert date format from DD.MM.YYYY to YYYY-MM-DD
                    date_issued = issue['Date of issue']
                    if date_issued:
                        parts = date_issued.split('.')
                        if len(parts) == 3:
                            date_issued = f"{parts[2]}-{parts[1]}-{parts[0]}"

                    date_return = issue['Return date']
                    status = 'returned'
                    if date_return:
                        parts = date_return.split('.')
                        if len(parts) == 3:
                            date_return = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    else:
                        date_return = None
                        status = 'issued'

                    cursor.execute('''
                        INSERT INTO issues (book_id, book_title, customer_id, customer_name, date_issued, date_return, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        issue['Book ID'],
                        issue['Book'],
                        issue['Customer ID'],
                        issue['Customer'],
                        date_issued,
                        date_return,
                        status
                    ))
        
        conn.commit()


def migrate_to_new_structure():
    """Migrate existing data to new structure"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("Starting data migration to new structure...")
        
        # 0. Migrate old book_themes structure if it uses theme_id
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='book_themes' AND column_name='theme_id'
        ''')
        old_structure = cursor.fetchone()
        
        if old_structure:
            print("Migrating book_themes from old structure (theme_id) to new structure (theme_name)...")
            
            # Check if themes table exists
            cursor.execute('''
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'themes'
                ) as exists
            ''')
            result = cursor.fetchone()
            themes_exists = result['exists'] if result else False
            
            if themes_exists:
                # Get theme mappings from old structure
                cursor.execute('''
                    SELECT DISTINCT bt.book_id, t.name as theme_name
                    FROM book_themes bt
                    INNER JOIN themes t ON bt.theme_id = t.id
                ''')
                theme_mappings = cursor.fetchall()
                
                # Drop old book_themes table
                cursor.execute('DROP TABLE IF EXISTS book_themes CASCADE')
                
                # Create new book_themes table
                cursor.execute('''
                    CREATE TABLE book_themes (
                        id SERIAL PRIMARY KEY,
                        book_id VARCHAR(50) NOT NULL,
                        theme_name VARCHAR(255) NOT NULL,
                        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                        UNIQUE(book_id, theme_name)
                    )
                ''')
                
                # Insert migrated data
                migrated_count = 0
                for mapping in theme_mappings:
                    try:
                        cursor.execute('''
                            INSERT INTO book_themes (book_id, theme_name)
                            VALUES (%s, %s)
                            ON CONFLICT (book_id, theme_name) DO NOTHING
                        ''', (mapping['book_id'], mapping['theme_name']))
                        migrated_count += 1
                    except Exception as e:
                        print(f"Error migrating theme mapping: {e}")
                
                print(f"[OK] Migrated {migrated_count} theme mappings from old structure")
            else:
                # No themes table, just recreate book_themes
                cursor.execute('DROP TABLE IF EXISTS book_themes CASCADE')
                cursor.execute('''
                    CREATE TABLE book_themes (
                        id SERIAL PRIMARY KEY,
                        book_id VARCHAR(50) NOT NULL,
                        theme_name VARCHAR(255) NOT NULL,
                        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                        UNIQUE(book_id, theme_name)
                    )
                ''')
        
        # Drop themes table if it still exists
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'themes'
            ) as exists
        ''')
        result = cursor.fetchone()
        if result and result['exists']:
            print("Dropping themes table...")
            cursor.execute('DROP TABLE IF EXISTS themes CASCADE')
            print("[OK] Themes table dropped")
        
        # 1. Migrate categories to book_themes (store theme name directly)
        cursor.execute('SELECT id, category FROM books WHERE category IS NOT NULL AND category != \'\'')
        books_with_categories = cursor.fetchall()
        
        migrated_categories = 0
        for book_row in books_with_categories:
            book_id = book_row['id']
            category = book_row['category']
            if category:
                # Check if link already exists
                cursor.execute('''
                    SELECT id FROM book_themes WHERE book_id = %s AND theme_name = %s
                ''', (book_id, category))
                if not cursor.fetchone():
                    try:
                        cursor.execute('''
                            INSERT INTO book_themes (book_id, theme_name) VALUES (%s, %s)
                            ON CONFLICT (book_id, theme_name) DO NOTHING
                        ''', (book_id, category))
                        migrated_categories += 1
                    except Exception as e:
                        print(f"Error adding theme for book {book_id}: {e}")
        
        print(f"[OK] Migrated {migrated_categories} book categories to book_themes")
        
        # 3. Migrate authors from old author field to new authors table
        cursor.execute('''
            SELECT DISTINCT author 
            FROM books 
            WHERE author IS NOT NULL AND author != ''
        ''')
        authors = cursor.fetchall()
        
        author_map = {}  # Map old author name to new author ID
        for auth_row in authors:
            author_name = auth_row['author']
            if author_name:
                # Check if author already exists
                cursor.execute('SELECT id FROM authors WHERE full_name = %s', (author_name,))
                existing = cursor.fetchone()
                if existing:
                    author_map[author_name] = existing['id']
                else:
                    # Create new author
                    cursor.execute('INSERT INTO authors (full_name) VALUES (%s) RETURNING id', (author_name,))
                    new_author = cursor.fetchone()
                    author_map[author_name] = new_author['id']
        
        print(f"[OK] Migrated {len(author_map)} authors to new authors table")
        
        # 4. Link books to authors
        cursor.execute('SELECT id, author FROM books WHERE author IS NOT NULL AND author != \'\'')
        books_with_authors = cursor.fetchall()
        
        for book_row in books_with_authors:
            book_id = book_row['id']
            author_name = book_row['author']
            if author_name in author_map:
                author_id = author_map[author_name]
                # Check if link already exists
                cursor.execute('''
                    SELECT id FROM book_authors WHERE book_id = %s AND author_id = %s
                ''', (book_id, author_id))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO book_authors (book_id, author_id) VALUES (%s, %s)
                    ''', (book_id, author_id))
        
        print(f"[OK] Linked {len(books_with_authors)} books to authors")
        
        # 5. Migrate cover_image to book_covers table
        cursor.execute('SELECT id, cover_image FROM books WHERE cover_image IS NOT NULL AND cover_image != \'\'')
        books_with_covers = cursor.fetchall()
        
        for book_row in books_with_covers:
            book_id = book_row['id']
            cover_image = book_row['cover_image']
            if cover_image:
                # Check if cover already exists
                cursor.execute('SELECT id FROM book_covers WHERE book_id = %s', (book_id,))
                if not cursor.fetchone():
                    # Extract filename from URL or use as-is
                    file_name = cover_image.split('/')[-1] if '/' in cover_image else cover_image
                    cursor.execute('''
                        INSERT INTO book_covers (book_id, file_name) VALUES (%s, %s)
                    ''', (book_id, file_name))
        
        print(f"[OK] Migrated {len(books_with_covers)} book covers")
        
        conn.commit()
        print("[OK] Data migration completed successfully!")
