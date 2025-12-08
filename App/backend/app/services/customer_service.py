"""
Customer Service - Business logic for customer operations
"""
from typing import List, Optional
from app.models import Customer
from app.repositories import CustomerRepository


class CustomerService:
    """Service for customer business logic"""
    
    @staticmethod
    def get_all_customers() -> List[Customer]:
        """Get all customers"""
        return CustomerRepository.find_all()
    
    @staticmethod
    def get_customer_by_id(customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        return CustomerRepository.find_by_id(customer_id)
    
    @staticmethod
    def search_customers(search_term: str) -> List[Customer]:
        """Search customers"""
        if not search_term:
            return CustomerRepository.find_all()
        return CustomerRepository.search(search_term)
    
    @staticmethod
    def create_customer(customer_data: dict) -> tuple[bool, str]:
        """
        Create a new customer
        Returns: (success: bool, message: str)
        """
        # Validate required fields
        if not customer_data.get('name'):
            return False, "Customer name is required"
        
        # Generate ID automatically if not provided
        if not customer_data.get('id'):
            customer_data['id'] = CustomerRepository.generate_unique_id()
        else:
            # Check if customer already exists (only if ID was provided)
            existing = CustomerRepository.find_by_id(customer_data['id'])
            if existing:
                return False, "Customer with this ID already exists"
        
        # Create customer
        customer = Customer.from_dict(customer_data)
        success = CustomerRepository.create(customer)
        
        if success:
            return True, f"Customer created successfully with ID: {customer_data['id']}"
        return False, "Failed to create customer"
    
    @staticmethod
    def update_customer(customer_data: dict) -> tuple[bool, str]:
        """
        Update customer
        Returns: (success: bool, message: str)
        """
        customer_id = customer_data.get('id')
        if not customer_id:
            return False, "Customer ID is required"
        
        # Check if customer exists
        existing = CustomerRepository.find_by_id(customer_id)
        if not existing:
            return False, "Customer not found"
        
        # Update customer
        customer = Customer.from_dict(customer_data)
        success = CustomerRepository.update(customer)
        
        if success:
            return True, "Customer updated successfully"
        return False, "Failed to update customer"
    
    @staticmethod
    def delete_customer(customer_id: str) -> tuple[bool, str]:
        """
        Delete customer
        Returns: (success: bool, message: str)
        """
        # Check if customer exists
        existing = CustomerRepository.find_by_id(customer_id)
        if not existing:
            return False, "Customer not found"
        
        # TODO: Check if customer has active issues
        
        success = CustomerRepository.delete(customer_id)
        
        if success:
            return True, "Customer deleted successfully"
        return False, "Failed to delete customer"


