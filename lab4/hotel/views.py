from asgiref.sync import sync_to_async
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .forms import AvailabilityForm, BookingForm
from .models import Booking
from .services import BookingService


class RoomListView(View):
    async def get(self, request):
        form = await sync_to_async(AvailabilityForm, thread_sensitive=True)(request.GET or None)
        rooms = []
        if request.GET:
            is_valid = await sync_to_async(form.is_valid, thread_sensitive=True)()
            if is_valid:
                rooms = await BookingService.get_available_rooms_async(
                    check_in_date=form.cleaned_data['check_in_date'],
                    check_out_date=form.cleaned_data['check_out_date'],
                    hotel=form.cleaned_data.get('hotel'),
                    min_capacity=form.cleaned_data['min_capacity'],
                )
        return await sync_to_async(render, thread_sensitive=True)(
            request,
            'hotel/room_list.html',
            {
                'form': form,
                'rooms': rooms,
                'search_performed': bool(request.GET),
            },
        )


class BookingCreateView(View):
    async def get(self, request):
        form = await sync_to_async(BookingForm, thread_sensitive=True)()
        return await sync_to_async(render, thread_sensitive=True)(request, 'hotel/booking_create.html', {'form': form})

    async def post(self, request):
        form = await sync_to_async(BookingForm, thread_sensitive=True)(request.POST)
        is_valid = await sync_to_async(form.is_valid, thread_sensitive=True)()
        if not is_valid:
            messages.error(request, 'Please correct the errors below')
            return await sync_to_async(render, thread_sensitive=True)(request, 'hotel/booking_create.html', {'form': form})

        try:
            booking = await BookingService.create_booking_async(
                room=form.cleaned_data['room'],
                client=form.cleaned_data['client'],
                services=form.cleaned_data.get('services'),
                check_in_date=form.cleaned_data['check_in_date'],
                check_out_date=form.cleaned_data['check_out_date'],
                status=form.cleaned_data['status'],
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return await sync_to_async(render, thread_sensitive=True)(request, 'hotel/booking_create.html', {'form': form})

        messages.success(request, f'Booking #{booking.id} was created successfully')
        return HttpResponseRedirect(reverse('hotel:booking_list'))


class BookingDeleteView(View):
    async def post(self, request, pk):
        booking = await Booking.objects.filter(pk=pk).afirst()
        if booking is None:
            raise Http404('Booking not found')

        await BookingService.delete_booking_async(booking)
        messages.success(request, f'Booking #{pk} deleted successfully')
        return HttpResponseRedirect(reverse('hotel:booking_list'))


class BookingListView(View):
    async def get(self, request):
        queryset = Booking.objects.select_related('room__hotel', 'client').prefetch_related('services').order_by('-created_at')
        bookings = [booking async for booking in queryset]
        return await sync_to_async(render, thread_sensitive=True)(request, 'hotel/booking_list.html', {'bookings': bookings})


class BookingDetailView(View):
    async def get(self, request, pk):
        booking = await Booking.objects.select_related('room__hotel', 'client').prefetch_related('services').filter(pk=pk).afirst()
        if booking is None:
            raise Http404('Booking not found')
        return await sync_to_async(render, thread_sensitive=True)(request, 'hotel/booking_detail.html', {'booking': booking})
