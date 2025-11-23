"""
Authentication Service - Business logic for authentication
"""
from typing import Optional, Tuple
from app.models import User, Customer
from app.repositories import UserRepository, CustomerRepository
from app.utils.jwt_utils import generate_token


class AuthService:
    """Service for authentication business logic"""
    
    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate user
        Returns: (success: bool, user: User, message: str)
        """
        if not email or not password:
            return False, None, "Email и пароль обязательны"
        
        # Find user by email
        user = UserRepository.find_by_email(email)
        if not user:
            return False, None, "Неверный email или пароль"
        
        # Check password
        if not user.check_password(password):
            return False, None, "Неверный email или пароль"
        
        return True, user, "Успешный вход"
    
    @staticmethod
    def register(email: str, password: str, name: str) -> Tuple[bool, Optional[User], str]:
        """
        Register new user (always as regular user, not admin)
        Returns: (success: bool, user: User, message: str)
        """
        # Validate input
        if not email or not password or not name:
            return False, None, "Все поля обязательны для заполнения"
        
        if len(password) < 6:
            return False, None, "Пароль должен быть минимум 6 символов"
        
        # Check if email exists
        if UserRepository.email_exists(email):
            return False, None, "Email уже зарегистрирован"
        
        # Create customer first
        # Generate customer ID
        import random
        import string
        customer_id = 'C' + ''.join(random.choices(string.digits, k=4))
        
        # Check if customer ID is unique
        while CustomerRepository.find_by_id(customer_id):
            customer_id = 'C' + ''.join(random.choices(string.digits, k=4))
        
        # Create customer
        customer = Customer(
            id=customer_id,
            name=name,
            email=email
        )
        
        if not CustomerRepository.create(customer):
            return False, None, "Ошибка создания профиля читателя"
        
        # Create user account (always as 'user' role, never 'admin')
        user = User(
            id=None,
            email=email,
            password_hash=User.hash_password(password),
            role='user',  # Always user, never admin
            customer_id=customer_id,
            name=name
        )
        
        user_id = UserRepository.create(user)
        if not user_id:
            # Rollback - delete customer
            CustomerRepository.delete(customer_id)
            return False, None, "Ошибка создания аккаунта"
        
        user.id = user_id
        return True, user, "Регистрация успешна"
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        return UserRepository.find_by_id(user_id)
    
    @staticmethod
    def generate_user_token(user: User) -> str:
        """
        Generate JWT token for user
        Returns: JWT token string
        """
        return generate_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            customer_id=user.customer_id,
            name=user.name
        )








