from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Room(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    room_number = models.CharField(
        max_length=10,
        unique=True,
        help_text='Unique room identifier'
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Maximum number of guests'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rooms'
        ordering = ['room_number']
        indexes = [
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Room {self.room_number} (Capacity: {self.capacity})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    guest_name = models.CharField(max_length=255)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_bookings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Booking {self.id} - {self.guest_name} - Room {self.room.room_number}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.check_in_date and self.check_out_date:
            if self.check_out_date < self.check_in_date:
                raise ValidationError('Check-out date must be after check-in date')
