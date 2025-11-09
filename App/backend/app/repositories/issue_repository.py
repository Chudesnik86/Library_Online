"""
Issue Repository - Data access layer for book issues (loans)
"""
from typing import List, Optional
from datetime import datetime
from app.database import get_db_connection
from app.models import Issue


class IssueRepository:
    """Repository for book issue data access"""
    
    @staticmethod
    def find_all() -> List[Issue]:
        """Get all issues"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM issues ORDER BY date_issued DESC')
            rows = cursor.fetchall()
            return [Issue.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_active() -> List[Issue]:
        """Get all active (not returned) issues"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM issues
                WHERE status = 'issued'
                ORDER BY date_issued DESC
            ''')
            rows = cursor.fetchall()
            return [Issue.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_customer(customer_id: str) -> List[Issue]:
        """Find all issues for a specific customer"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM issues
                WHERE customer_id = ?
                ORDER BY date_issued DESC
            ''', (customer_id,))
            rows = cursor.fetchall()
            return [Issue.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_active_by_customer(customer_id: str) -> List[Issue]:
        """Find active issues for a specific customer"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM issues
                WHERE customer_id = ? AND status = 'issued'
                ORDER BY date_issued DESC
            ''', (customer_id,))
            rows = cursor.fetchall()
            return [Issue.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def find_by_id(issue_id: int) -> Optional[Issue]:
        """Find issue by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
            row = cursor.fetchone()
            return Issue.from_dict(dict(row)) if row else None
    
    @staticmethod
    def create(issue: Issue) -> Optional[int]:
        """Create a new issue"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO issues (book_id, book_title, customer_id, customer_name, date_issued, date_return, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    issue.book_id,
                    issue.book_title,
                    issue.customer_id,
                    issue.customer_name,
                    issue.date_issued,
                    issue.date_return,
                    issue.status
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
    
    @staticmethod
    def return_book(issue_id: int, return_date: str = None) -> bool:
        """Mark an issue as returned"""
        if return_date is None:
            return_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE issues
                    SET date_return = ?, status = 'returned'
                    WHERE id = ?
                ''', (return_date, issue_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error returning book: {e}")
            return False
    
    @staticmethod
    def search(search_term: str) -> List[Issue]:
        """Search issues by book title, customer name, or customer ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT * FROM issues
                WHERE book_title LIKE ? OR customer_name LIKE ? OR customer_id LIKE ?
                ORDER BY date_issued DESC
            '''
            pattern = f'%{search_term}%'
            cursor.execute(query, (pattern, pattern, pattern))
            rows = cursor.fetchall()
            return [Issue.from_dict(dict(row)) for row in rows]
    
    @staticmethod
    def get_overdue() -> List[Issue]:
        """Get all overdue issues"""
        issues = IssueRepository.find_active()
        return [issue for issue in issues if issue.is_overdue]
    
    @staticmethod
    def get_statistics() -> dict:
        """Get statistics about issues"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total issues
            cursor.execute('SELECT COUNT(*) FROM issues')
            stats['total_issues'] = cursor.fetchone()[0]
            
            # Active issues
            cursor.execute("SELECT COUNT(*) FROM issues WHERE status='issued'")
            stats['active_issues'] = cursor.fetchone()[0]
            
            # Most active customers
            cursor.execute('''
                SELECT customer_name, customer_id, COUNT(*) as count
                FROM issues
                GROUP BY customer_id
                ORDER BY count DESC
                LIMIT 5
            ''')
            stats['top_customers'] = [dict(row) for row in cursor.fetchall()]
            
            # Most borrowed books
            cursor.execute('''
                SELECT book_title, book_id, COUNT(*) as count
                FROM issues
                GROUP BY book_id
                ORDER BY count DESC
                LIMIT 5
            ''')
            stats['top_books'] = [dict(row) for row in cursor.fetchall()]
            
            return stats


