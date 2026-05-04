from django.contrib.auth import authenticate as django_authenticate
from django.db import transaction
from .models import User

class AuthService:
    @staticmethod
    def authenticate(username, raw_password):
        return django_authenticate(username=username, password=raw_password)
    
    @staticmethod
    @transaction.atomic
    def register_user(username, email, raw_password, role='CONCIERGE', **extra_fields):
        valid_roles = ['CONCIERGE', 'ADMIN']
        if role not in valid_roles:
            raise ValueError(f"Invalid role '{role}'. Must be one of {valid_roles}")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=raw_password,
            role=role,
            **extra_fields
        )
        
        return user
    
    @staticmethod
    def get_user_by_username(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
