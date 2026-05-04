from django.db import models
from django.conf import settings
from django.utils import timezone


class Guest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    identification_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Passport or ID number'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'guests'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class VisitLog(models.Model):
    guest = models.ForeignKey(
        'Guest',
        on_delete=models.PROTECT,
        related_name='visit_logs'
    )
    room = models.ForeignKey(
        'inventory.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visit_logs',
        help_text='Room assignment during visit'
    )
    entry_time = models.DateTimeField(
        default=timezone.now,
        help_text='When guest entered premises'
    )
    exit_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When guest left premises (NULL = still present)'
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_visits',
        help_text='Concierge who processed this entry'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the visit'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'visit_logs'
        ordering = ['-entry_time']
        indexes = [
            models.Index(fields=['entry_time']),
            models.Index(fields=['exit_time']),
            models.Index(fields=['-entry_time']),
        ]
    
    def __str__(self):
        status = "Active" if self.exit_time is None else "Completed"
        return f"{self.guest.full_name} - {status} ({self.entry_time.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def is_active(self):
        return self.exit_time is None
    
    @property
    def duration(self):
        if self.exit_time:
            return self.exit_time - self.entry_time
        return None
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.exit_time and self.entry_time:
            if self.exit_time < self.entry_time:
                raise ValidationError('Exit time must be after entry time')
