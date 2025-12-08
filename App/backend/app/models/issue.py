"""
Issue (Book Loan) model
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date


@dataclass
class Issue:
    """Book loan entity"""
    id: Optional[int]
    book_id: str
    book_title: str
    customer_id: str
    customer_name: str
    date_issued: str
    date_return: Optional[str] = None
    status: str = 'issued'  # 'issued' or 'returned'
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Issue from dictionary"""
        # Handle dates - PostgreSQL returns date objects, not strings
        date_issued = data.get('date_issued')
        if date_issued and not isinstance(date_issued, str):
            # Convert date object to string
            if hasattr(date_issued, 'isoformat'):
                date_issued = date_issued.isoformat()
            else:
                date_issued = str(date_issued)
        
        date_return = data.get('date_return')
        if date_return and not isinstance(date_return, str):
            # Convert date object to string
            if hasattr(date_return, 'isoformat'):
                date_return = date_return.isoformat()
            else:
                date_return = str(date_return)
        
        return cls(
            id=data.get('id'),
            book_id=data['book_id'],
            book_title=data['book_title'],
            customer_id=data['customer_id'],
            customer_name=data['customer_name'],
            date_issued=date_issued or '',
            date_return=date_return,
            status=data.get('status', 'issued')
        )
    
    def to_dict(self):
        """Convert Issue to dictionary"""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book_title,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'date_issued': self.date_issued,
            'date_return': self.date_return,
            'status': self.status
        }
    
    @property
    def is_overdue(self) -> bool:
        """Check if the book is overdue (>14 days)"""
        if self.status == 'returned':
            return False
        
        from config import LOAN_PERIOD_DAYS
        try:
            # Handle both string and date object
            if isinstance(self.date_issued, str):
                issued_date = datetime.strptime(self.date_issued, '%Y-%m-%d')
            elif hasattr(self.date_issued, 'isoformat'):
                # It's a date object
                issued_date = datetime.combine(self.date_issued, datetime.min.time())
            else:
                return False
            
            days_out = (datetime.now() - issued_date).days
            return days_out > LOAN_PERIOD_DAYS
        except:
            return False
    
    @property
    def days_borrowed(self) -> int:
        """Get number of days the book has been borrowed"""
        try:
            # Handle both string and date object
            if isinstance(self.date_issued, str):
                issued_date = datetime.strptime(self.date_issued, '%Y-%m-%d')
            elif hasattr(self.date_issued, 'isoformat'):
                # It's a date object
                issued_date = datetime.combine(self.date_issued, datetime.min.time())
            else:
                return 0
            
            if self.status == 'returned' and self.date_return:
                if isinstance(self.date_return, str):
                    return_date = datetime.strptime(self.date_return, '%Y-%m-%d')
                elif hasattr(self.date_return, 'isoformat'):
                    return_date = datetime.combine(self.date_return, datetime.min.time())
                else:
                    return 0
                return (return_date - issued_date).days
            else:
                return (datetime.now() - issued_date).days
        except:
            return 0


