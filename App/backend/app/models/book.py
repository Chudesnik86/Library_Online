"""
Book model
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Book:
    """Book entity - Книга"""
    id: str
    title: str  # Название
    subtitle: Optional[str] = None  # Подзаголовок
    description: Optional[str] = None  # Описание/Аннотация
    publication_year: Optional[int] = None  # Дата первой публикации (год)
    isbn: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1
    
    # Legacy fields for backward compatibility
    author: Optional[str] = None  # Старое поле, для совместимости
    category: Optional[str] = None  # Старое поле, для совместимости
    cover_image: Optional[str] = None  # Старое поле, для совместимости
    
    # New fields for multiple authors
    author_names: Optional[List[str]] = None  # Список имен авторов
    authors_info: Optional[List[dict]] = None  # Полная информация об авторах (id, full_name, wikipedia_url)
    
    # New fields for multiple covers
    covers: Optional[List[dict]] = None  # Список обложек (id, book_id, file_name)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Book from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            subtitle=data.get('subtitle'),
            description=data.get('description'),
            publication_year=data.get('publication_year'),
            isbn=data.get('isbn'),
            total_copies=data.get('total_copies', 1),
            available_copies=data.get('available_copies', 1),
            # Legacy fields
            author=data.get('author'),
            category=data.get('category'),
            cover_image=data.get('cover_image'),
            # New fields
            author_names=data.get('author_names'),
            authors_info=data.get('authors_info'),
            covers=data.get('covers')
        )
    
    def to_dict(self):
        """Convert Book to dictionary"""
        # Format authors as comma-separated string for display
        # Only use author_names if available, don't use legacy author field if author_names exists
        authors_display = None
        if self.author_names and len(self.author_names) > 0:
            authors_display = ', '.join(self.author_names)
        elif self.author:  # Fallback to legacy field only if no author_names
            authors_display = self.author
        
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'description': self.description,
            'publication_year': self.publication_year,
            'isbn': self.isbn,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            # Legacy fields for backward compatibility
            # Only set author if we have author_names, otherwise use legacy field
            'author': authors_display if (self.author_names and len(self.author_names) > 0) else (self.author or ''),
            'category': self.category,
            'cover_image': self.cover_image,
            # New fields
            'author_names': self.author_names or [],
            'authors_info': self.authors_info or [],
            'covers': self.covers or []
        }
    
    @property
    def is_available(self) -> bool:
        """Check if book is available for borrowing"""
        return self.available_copies > 0


