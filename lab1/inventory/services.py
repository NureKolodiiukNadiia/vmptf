from django.db import transaction
from django.db.models import Q
from .models import Room, Booking


class BookingService:
    @staticmethod
    def check_room_availability(room, check_in_date, check_out_date, exclude_booking_id=None):
        overlapping_bookings = Booking.objects.filter(
            room=room,
            status__in=['PENDING', 'CONFIRMED']
        ).filter(
            Q(check_in_date__lt=check_out_date) &
            Q(check_out_date__gt=check_in_date)
        )
        
        if exclude_booking_id:
            overlapping_bookings = overlapping_bookings.exclude(id=exclude_booking_id)
        
        return not overlapping_bookings.exists()
    
    @staticmethod
    @transaction.atomic
    def create_booking(room, guest_name, check_in_date, check_out_date, 
                      created_by=None, guest_email='', guest_phone='', **kwargs):
        if check_out_date < check_in_date:
            raise ValueError('Check-out date must be after or equal to check-in date')
        
        room_locked = Room.objects.select_for_update().get(pk=room.pk)
        if not BookingService.check_room_availability(room_locked, check_in_date, check_out_date):
            raise ValueError(
                f'Room {room.room_number} is not available for the selected dates'
            )
        
        booking = Booking.objects.create(
            room=room_locked,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            created_by=created_by,
            **kwargs
        )
        
        return booking
    
    @staticmethod
    def get_available_rooms(check_in_date, check_out_date, min_capacity=1):
        conflicting_rooms = Booking.objects.filter(
            status__in=['PENDING', 'CONFIRMED'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        ).values_list('room_id', flat=True)
        
        return Room.objects.filter(
            capacity__gte=min_capacity,
            status='AVAILABLE'
        ).exclude(
            id__in=conflicting_rooms
        )
    
    @staticmethod
    def cancel_booking(booking):
        if booking.status in ['CANCELLED', 'COMPLETED']:
            raise ValueError(f'Cannot cancel a {booking.status.lower()} booking')
        
        booking.status = 'CANCELLED'
        booking.save(update_fields=['status'])
        return booking
