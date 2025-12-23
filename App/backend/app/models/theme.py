"""
Theme model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Theme:
    """Theme entity - тематическая категория"""
    id: Optional[int] = None
    name: str = ""  # Наименование темы
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Theme from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', '')
        )
    
    def to_dict(self):
        """Convert Theme to dictionary"""
        return {
            'id': self.id,
            'name': self.name
        }



