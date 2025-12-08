"""
Exhibition model
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import date


@dataclass
class Exhibition:
    """Exhibition entity"""
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Exhibition from dictionary"""
        # Handle dates - PostgreSQL returns date objects, not strings
        start_date = data.get('start_date')
        if start_date:
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            elif isinstance(start_date, date):
                start_date = start_date
            else:
                start_date = None
        else:
            start_date = None
        
        end_date = data.get('end_date')
        if end_date:
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            elif isinstance(end_date, date):
                end_date = end_date
            else:
                end_date = None
        else:
            end_date = None
        
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            is_active=bool(data.get('is_active', True)),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert Exhibition to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    def is_currently_active(self) -> bool:
        """Check if exhibition is currently active based on dates"""
        if not self.is_active:
            return False
        
        today = date.today()
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        
        return True

