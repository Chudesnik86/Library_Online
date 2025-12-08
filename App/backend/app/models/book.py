"""
Book model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Book entity"""
    id: str
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1
    description: Optional[str] = None
    cover_image: Optional[str] = None  # URL to cover image
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Book from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            author=data.get('author'),
            isbn=data.get('isbn'),
            category=data.get('category'),
            total_copies=data.get('total_copies', 1),
            available_copies=data.get('available_copies', 1),
            description=data.get('description'),
            cover_image=data.get('cover_image')
        )
    
    def to_dict(self):
        """Convert Book to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'description': self.description,
            'cover_image': self.cover_image
        }
    
    @property
    def is_available(self) -> bool:
        """Check if book is available for borrowing"""
        return self.available_copies > 0


