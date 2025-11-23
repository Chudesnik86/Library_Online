"""
Configuration file for the Library Management System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'library.db')

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

# Sample data paths
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, 'C:/Users/LexCh/Downloads/test_project [ZUOs18]', 'sample_data')


