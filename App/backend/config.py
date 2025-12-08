"""
Configuration file for the Library Management System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# PostgreSQL Database configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'library_online'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '00000')
}

# Database connection string (for psycopg2)
def get_db_connection_string():
    """Get PostgreSQL connection string"""
    return "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DATABASE_CONFIG)

# Flask configuration
SECRET_KEY = 'library-online-secret-key-2024'
DEBUG = True

# JWT configuration
JWT_SECRET_KEY = 'library-online-jwt-secret-key-2024'  # Should be different from SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# Application settings
LOAN_PERIOD_DAYS = 14  # Standard loan period
MAX_BOOKS_PER_USER = 5  # Maximum books a user can borrow at once

# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size for Excel uploads

# Sample data paths
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, 'C:/Users/LexCh/Downloads/test_project [ZUOs18]', 'sample_data')


