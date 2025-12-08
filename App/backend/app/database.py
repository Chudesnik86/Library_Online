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
        
        # Books table (no dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                author VARCHAR(255),
                isbn VARCHAR(50),
                category VARCHAR(255),
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                description TEXT,
                cover_image TEXT
            )
        ''')
        
        # Migrate existing books table to add new columns if they don't exist
        # PostgreSQL doesn't support IF NOT EXISTS for ALTER TABLE, so we check first
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='books' AND column_name='description'
        ''')
        if not cursor.fetchone():
            cursor.execute('ALTER TABLE books ADD COLUMN description TEXT')
        
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='books' AND column_name='cover_image'
        ''')
        if not cursor.fetchone():
            cursor.execute('ALTER TABLE books ADD COLUMN cover_image TEXT')
        
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
                status VARCHAR(50) DEFAULT 'issued'
            )
        ''')
        
        # Add foreign key constraints for issues if they don't exist
        cursor.execute('''
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='issues' 
            AND constraint_type='FOREIGN KEY'
            AND constraint_name LIKE '%book_id%'
        ''')
        if not cursor.fetchone():
            cursor.execute('''
                ALTER TABLE issues 
                ADD CONSTRAINT fk_issues_book_id 
                FOREIGN KEY (book_id) REFERENCES books(id)
            ''')
        
        cursor.execute('''
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='issues' 
            AND constraint_type='FOREIGN KEY'
            AND constraint_name LIKE '%customer_id%'
        ''')
        if not cursor.fetchone():
            cursor.execute('''
                ALTER TABLE issues 
                ADD CONSTRAINT fk_issues_customer_id 
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            ''')
        
        # Exhibition books (depends on exhibitions and books)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exhibition_books (
                id SERIAL PRIMARY KEY,
                exhibition_id INTEGER NOT NULL,
                book_id VARCHAR(50) NOT NULL,
                display_order INTEGER DEFAULT 0,
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
        
        conn.commit()


def create_default_admin():
    """Create default admin user if not exists"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='admin'")
        result = cursor.fetchone()
        if (result[0] if isinstance(result, tuple) else result['count']) == 0:
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
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) as count FROM customers')
        result = cursor.fetchone()
        if (result[0] if isinstance(result, tuple) else result['count']) > 0:
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
