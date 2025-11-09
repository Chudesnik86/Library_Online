"""
Customer model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    """Customer entity"""
    id: str
    name: str
    address: Optional[str] = None
    zip: Optional[int] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Customer from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            address=data.get('address'),
            zip=data.get('zip'),
            city=data.get('city'),
            phone=data.get('phone'),
            email=data.get('email')
        )
    
    def to_dict(self):
        """Convert Customer to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'zip': self.zip,
            'city': self.city,
            'phone': self.phone,
            'email': self.email
        }


