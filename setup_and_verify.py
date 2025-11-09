#!/usr/bin/env python3
"""
Library Online Management System - Setup and Verification Script
Verifies installation, checks dependencies, and prepares the application
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_check(status, message):
    """Print check result"""
    symbol = "+" if status else "X"
    status_text = "OK" if status else "FAIL"
    print(f"[{symbol}] {message:<45} [{status_text}]")


def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")
    version = sys.version_info
    required = (3, 7)
    
    current = f"{version.major}.{version.minor}.{version.micro}"
    required_str = f"{required[0]}.{required[1]}+"
    
    status = version >= required
    print_check(status, f"Python {required_str} (Current: {current})")
    
    if not status:
        print(f"\n[WARNING] Python {required_str} is required!")
        print(f"   Current version: {current}")
        print(f"   Please upgrade Python from https://python.org")
        return False
    
    return True


def check_tkinter():
    """Check if tkinter is available"""
    print_header("Checking GUI Framework")
    
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        print_check(True, "tkinter (GUI framework)")
        
        # Test creating a window
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print_check(True, "tkinter window creation test")
        
        return True
    except ImportError as e:
        print_check(False, "tkinter (GUI framework)")
        print(f"\n[ERROR] {e}")
        print("\nInstallation instructions:")
        print("  - Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  - Fedora: sudo dnf install python3-tkinter")
        print("  - macOS: Already included with Python")
        print("  - Windows: Already included with Python")
        return False


def check_standard_libraries():
    """Check standard library modules"""
    print_header("Checking Standard Libraries")
    
    modules = [
        ('sqlite3', 'Database engine'),
        ('json', 'JSON data handling'),
        ('csv', 'CSV data handling'),
        ('datetime', 'Date/time operations'),
        ('pathlib', 'File path handling'),
        ('os', 'Operating system interface'),
        ('shutil', 'File operations')
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print_check(True, f"{module_name:<15} ({description})")
        except ImportError:
            print_check(False, f"{module_name:<15} ({description})")
            all_ok = False
    
    return all_ok


def check_project_files():
    """Check if all project files exist"""
    print_header("Checking Project Files")
    
    required_files = [
        ('main.py', 'Main application'),
        ('database.py', 'Database handler'),
        ('run.py', 'Application launcher'),
        ('db_utils.py', 'Database utilities'),
        ('README.md', 'English documentation'),
        ('РУКОВОДСТВО_ПОЛЬЗОВАТЕЛЯ.md', 'Russian documentation'),
        ('QUICK_START.md', 'Quick start guide'),
        ('requirements.txt', 'Dependencies list')
    ]
    
    all_ok = True
    for filename, description in required_files:
        exists = os.path.exists(filename)
        print_check(exists, f"{filename:<30} ({description})")
        if not exists:
            all_ok = False
    
    return all_ok


def check_sample_data():
    """Check if sample data exists"""
    print_header("Checking Sample Data")
    
    sample_dir = Path("test_project [ZUOs18]/sample_data")
    
    if not sample_dir.exists():
        print_check(False, "Sample data directory")
        return False
    
    print_check(True, "Sample data directory")
    
    sample_files = [
        'Customers.json',
        'Issues.json'
    ]
    
    all_ok = True
    for filename in sample_files:
        file_path = sample_dir / filename
        exists = file_path.exists()
        print_check(exists, f"{filename:<30}")
        if not exists:
            all_ok = False
    
    return all_ok


def check_database():
    """Check database status"""
    print_header("Checking Database")
    
    db_file = "library.db"
    
    if os.path.exists(db_file):
        size = os.path.getsize(db_file) / 1024  # KB
        print_check(True, f"Database exists (Size: {size:.2f} KB)")
        
        # Try to connect
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['Customers', 'Books', 'Issues']
            for table in expected_tables:
                exists = table in tables
                print_check(exists, f"Table: {table}")
            
            # Get record counts
            cursor.execute("SELECT COUNT(*) FROM Customers")
            customer_count = cursor.fetchone()[0]
            print_check(True, f"Customers: {customer_count} records")
            
            cursor.execute("SELECT COUNT(*) FROM Books")
            book_count = cursor.fetchone()[0]
            print_check(True, f"Books: {book_count} records")
            
            cursor.execute("SELECT COUNT(*) FROM Issues")
            issue_count = cursor.fetchone()[0]
            print_check(True, f"Issues: {issue_count} records")
            
            conn.close()
            return True
            
        except Exception as e:
            print_check(False, f"Database connection: {e}")
            return False
    else:
        print_check(True, "Database will be created on first run")
        return True


def test_import():
    """Test importing application modules"""
    print_header("Testing Application Import")
    
    try:
        from database import LibraryDatabase
        print_check(True, "Import database module")
        
        # Test database initialization
        db = LibraryDatabase("test_verify.db")
        print_check(True, "Initialize database")
        
        # Test adding customer
        success = db.add_customer("TEST001", "Test User", "Test Address", 12345, "Test City", "123-456-7890", "test@test.com")
        print_check(success, "Add test customer")
        
        # Test searching
        customers = db.search_customers("TEST001")
        print_check(len(customers) > 0, "Search customer")
        
        # Cleanup
        db.close()
        if os.path.exists("test_verify.db"):
            os.remove("test_verify.db")
        
        print_check(True, "Database operations test passed")
        return True
        
    except Exception as e:
        print_check(False, f"Import test: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_shortcuts():
    """Create convenience shortcuts if they don't exist"""
    print_header("Creating Shortcuts")
    
    # Windows batch file
    if sys.platform == "win32":
        if not os.path.exists("start.bat"):
            try:
                with open("start.bat", "w") as f:
                    f.write("@echo off\n")
                    f.write("python main.py\n")
                    f.write("pause\n")
                print_check(True, "Created start.bat (Windows launcher)")
            except:
                print_check(False, "Failed to create start.bat")
    
    # Unix shell script
    else:
        if not os.path.exists("start.sh"):
            try:
                with open("start.sh", "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write("python3 main.py\n")
                os.chmod("start.sh", 0o755)
                print_check(True, "Created start.sh (Unix launcher)")
            except:
                print_check(False, "Failed to create start.sh")


def print_summary(all_checks):
    """Print verification summary"""
    print_header("Verification Summary")
    
    if all(all_checks.values()):
        print("\n[OK] All checks passed!")
        print("   The application is ready to use.")
        print("\nTo start the application:")
        if sys.platform == "win32":
            print("   - Double-click 'start.bat'")
            print("   - Or run: python main.py")
        else:
            print("   - Run: python3 main.py")
            print("   - Or run: ./start.sh")
        print("\nDocumentation:")
        print("   - README.md (English)")
        print("   - QUICK_START.md (Quick guide)")
        print()
    else:
        print("\n[WARNING] Some checks failed!")
        print("   Please resolve the issues above before running the application.")
        print()
        
        failed = [name for name, status in all_checks.items() if not status]
        print("Failed checks:")
        for name in failed:
            print(f"   - {name}")
        print()


def main():
    """Main verification function"""
    print("\n" + "=" * 60)
    print("  Library Online Management System")
    print("  Setup and Verification Script")
    print("=" * 60)
    
    checks = {}
    
    # Run all checks
    checks['Python Version'] = check_python_version()
    checks['GUI Framework'] = check_tkinter()
    checks['Standard Libraries'] = check_standard_libraries()
    checks['Project Files'] = check_project_files()
    checks['Sample Data'] = check_sample_data()
    checks['Database'] = check_database()
    checks['Application Import'] = test_import()
    
    # Create shortcuts
    create_shortcuts()
    
    # Print summary
    print_summary(checks)
    
    # Return exit code
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

