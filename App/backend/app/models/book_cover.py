"""
Book Cover model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class BookCover:
    """Book Cover entity - обложка книги"""
    id: Optional[int] = None
    book_id: str = ""  # ID книги
    file_name: str = ""  # Имя файла обложки
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create BookCover from dictionary"""
        return cls(
            id=data.get('id'),
            book_id=data.get('book_id', ''),
            file_name=data.get('file_name', '')
        )
    
    def to_dict(self):
        """Convert BookCover to dictionary"""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'file_name': self.file_name
        }



