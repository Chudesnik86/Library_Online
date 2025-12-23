"""
Author model
"""
from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Author:
    """Author entity - автор книги"""
    id: Optional[int] = None
    full_name: str = ""  # ФИО автора
    birth_date: Optional[date] = None  # Дата рождения
    death_date: Optional[date] = None  # Дата смерти
    biography: Optional[str] = None  # Биография
    wikipedia_url: Optional[str] = None  # Ссылка на Wikipedia
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Author from dictionary"""
        # Handle dates - PostgreSQL returns date objects, not strings
        birth_date = data.get('birth_date')
        if birth_date:
            if isinstance(birth_date, str):
                birth_date = date.fromisoformat(birth_date)
            elif not isinstance(birth_date, date):
                birth_date = None
        else:
            birth_date = None
        
        death_date = data.get('death_date')
        if death_date:
            if isinstance(death_date, str):
                death_date = date.fromisoformat(death_date)
            elif not isinstance(death_date, date):
                death_date = None
        else:
            death_date = None
        
        return cls(
            id=data.get('id'),
            full_name=data.get('full_name', ''),
            birth_date=birth_date,
            death_date=death_date,
            biography=data.get('biography'),
            wikipedia_url=data.get('wikipedia_url')
        )
    
    def to_dict(self):
        """Convert Author to dictionary"""
        # Handle dates - convert to string if date object, otherwise keep as is
        birth_date = self.birth_date
        if birth_date and isinstance(birth_date, date):
            birth_date = birth_date.isoformat()
        elif birth_date and not isinstance(birth_date, str):
            birth_date = None
        
        death_date = self.death_date
        if death_date and isinstance(death_date, date):
            death_date = death_date.isoformat()
        elif death_date and not isinstance(death_date, str):
            death_date = None
        
        return {
            'id': self.id,
            'full_name': self.full_name,
            'birth_date': birth_date,
            'death_date': death_date,
            'biography': self.biography,
            'wikipedia_url': self.wikipedia_url
        }


