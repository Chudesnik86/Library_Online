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

# Application settings
LOAN_PERIOD_DAYS = 14  # Standard loan period
MAX_BOOKS_PER_USER = 5  # Maximum books a user can borrow at once

# Sample data paths
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, 'C:/Users/LexCh/Downloads/test_project [ZUOs18]', 'sample_data')


