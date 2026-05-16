from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotels'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.city})"


class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clients'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Room(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT, related_name='rooms')
    room_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rooms'
        ordering = ['hotel__name', 'room_number']
        constraints = [
            models.UniqueConstraint(fields=['hotel', 'room_number'], name='unique_room_per_hotel'),
        ]
        indexes = [models.Index(fields=['status']), models.Index(fields=['hotel'])]

    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number}"


class Service(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )

    class Meta:
        db_table = 'services'
        ordering = ['hotel__name', 'name']
        constraints = [
            models.UniqueConstraint(fields=['hotel', 'name'], name='unique_service_name_per_hotel'),
        ]

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='bookings')
    services = models.ManyToManyField(Service, blank=True, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
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
        return f"Booking {self.id} - {self.client} - {self.room}"

    def clean(self):
        if self.check_in_date and self.check_out_date and self.check_out_date <= self.check_in_date:
            raise ValidationError('Check-out date must be after check-in date')
