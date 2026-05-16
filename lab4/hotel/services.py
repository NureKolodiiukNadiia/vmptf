from decimal import Decimal

from asgiref.sync import sync_to_async
from django.db import transaction

from .models import Booking, Room


class BookingService:
    @staticmethod
    def check_room_availability(room, check_in_date, check_out_date, exclude_booking_id=None):
        overlapping = Booking.objects.filter(
            room=room,
            status__in=['PENDING', 'CONFIRMED'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
        )
        if exclude_booking_id:
            overlapping = overlapping.exclude(id=exclude_booking_id)
        return not overlapping.exists()

    @staticmethod
    async def check_room_availability_async(room, check_in_date, check_out_date, exclude_booking_id=None):
        overlapping = Booking.objects.filter(
            room=room,
            status__in=['PENDING', 'CONFIRMED'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
        )
        if exclude_booking_id:
            overlapping = overlapping.exclude(id=exclude_booking_id)
        return not await overlapping.aexists()

    @staticmethod
    def calculate_total_price(room, check_in_date, check_out_date):
        nights = (check_out_date - check_in_date).days
        return room.price_per_night * Decimal(max(nights, 0))

    @staticmethod
    @transaction.atomic
    def create_booking(room, client, check_in_date, check_out_date, services=None, **kwargs):
        if check_out_date <= check_in_date:
            raise ValueError('Check-out date must be after check-in date')

        room_locked = Room.objects.select_for_update().get(pk=room.pk)
        if not BookingService.check_room_availability(room_locked, check_in_date, check_out_date):
            raise ValueError(f'Room {room.room_number} is not available for selected dates')

        booking = Booking.objects.create(
            room=room_locked,
            client=client,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_price=BookingService.calculate_total_price(room_locked, check_in_date, check_out_date),
            **kwargs,
        )

        if services:
            booking.services.set(services)

        return booking

    @staticmethod
    async def create_booking_async(room, client, check_in_date, check_out_date, services=None, **kwargs):
        return await sync_to_async(BookingService.create_booking, thread_sensitive=True)(
            room=room,
            client=client,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            services=services,
            **kwargs,
        )

    @staticmethod
    @transaction.atomic
    def delete_booking(booking):
        booking.delete()

    @staticmethod
    async def delete_booking_async(booking):
        await booking.adelete()

    @staticmethod
    def get_available_rooms(check_in_date, check_out_date, hotel=None, min_capacity=1):
        conflicting_room_ids = Booking.objects.filter(
            status__in=['PENDING', 'CONFIRMED'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
        ).values_list('room_id', flat=True)

        qs = Room.objects.filter(status='AVAILABLE', capacity__gte=min_capacity).exclude(id__in=conflicting_room_ids)
        if hotel is not None:
            qs = qs.filter(hotel=hotel)
        return qs.select_related('hotel').order_by('hotel__name', 'room_number')

    @staticmethod
    async def get_available_rooms_async(check_in_date, check_out_date, hotel=None, min_capacity=1):
        conflicting_room_ids = [
            room_id
            async for room_id in Booking.objects.filter(
                status__in=['PENDING', 'CONFIRMED'],
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date,
            ).values_list('room_id', flat=True)
        ]

        qs = Room.objects.filter(status='AVAILABLE', capacity__gte=min_capacity).exclude(id__in=conflicting_room_ids)
        if hotel is not None:
            qs = qs.filter(hotel=hotel)

        return [room async for room in qs.select_related('hotel').order_by('hotel__name', 'room_number')]
