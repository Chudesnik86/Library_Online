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
        # Validate required fields
        if 'id' not in data:
            raise ValueError("Customer 'id' is required")
        if 'name' not in data or not data['name']:
            raise ValueError("Customer 'name' is required")
        
        return cls(
            id=str(data['id']),
            name=str(data['name']),
            address=str(data['address']) if data.get('address') else None,
            zip=int(data['zip']) if data.get('zip') is not None else None,
            city=str(data['city']) if data.get('city') else None,
            phone=str(data['phone']) if data.get('phone') else None,
            email=str(data['email']) if data.get('email') else None
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


