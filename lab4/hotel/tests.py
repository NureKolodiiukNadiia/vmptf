from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from .models import Booking, Client, Hotel, Room
from .services import BookingService


class BookingServiceTests(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name='Test Hotel', address='Main St 1', city='Kyiv')
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_number='101',
            capacity=2,
            price_per_night=Decimal('100.00'),
            status='AVAILABLE',
        )
        self.client = Client.objects.create(
            first_name='Ivan',
            last_name='Petrenko',
            email='ivan@example.com',
            phone='+380000000000',
        )

    def test_create_booking_sets_total_price(self):
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=3)

        booking = BookingService.create_booking(
            room=self.room,
            client=self.client,
            check_in_date=check_in,
            check_out_date=check_out,
        )

        self.assertEqual(booking.total_price, Decimal('300.00'))

    def test_overlapping_booking_not_available(self):
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        Booking.objects.create(
            room=self.room,
            client=self.client,
            check_in_date=check_in,
            check_out_date=check_out,
            status='CONFIRMED',
            total_price=Decimal('200.00'),
        )

        is_available = BookingService.check_room_availability(
            room=self.room,
            check_in_date=check_in + timedelta(days=1),
            check_out_date=check_out + timedelta(days=1),
        )

        self.assertFalse(is_available)
