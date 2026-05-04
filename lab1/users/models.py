from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('CONCIERGE', 'Concierge'),
        ('ADMIN', 'Administrator'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CONCIERGE',
        help_text='User role determines access permissions'
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
    
    def is_concierge(self):
        return self.role == 'CONCIERGE'
