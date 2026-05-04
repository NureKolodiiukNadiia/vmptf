from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.db import IntegrityError

from .models import Room, Booking
from .forms import BookingForm
from .services import BookingService


class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'inventory/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('room_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Room.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        return context


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'inventory/booking_create.html'
    success_url = reverse_lazy('inventory:booking_list')
    
    def form_valid(self, form):
        try:
            booking = BookingService.create_booking(
                room=form.cleaned_data['room'],
                guest_name=form.cleaned_data['guest_name'],
                guest_email=form.cleaned_data.get('guest_email', ''),
                guest_phone=form.cleaned_data.get('guest_phone', ''),
                check_in_date=form.cleaned_data['check_in_date'],
                check_out_date=form.cleaned_data['check_out_date'],
                created_by=self.request.user
            )
            
            messages.success(
                self.request,
                f'Booking created successfully for {booking.guest_name} '
                f'in room {booking.room.room_number}'
            )
            
            return redirect(self.success_url)
            
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        
        except IntegrityError as e:
            messages.error(self.request, 'Database error occurred. Please try again.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below')
        return super().form_invalid(form)


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'inventory/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('room', 'created_by')
        
        status = self.request.GET.get('status')
        room_id = self.request.GET.get('room')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Booking.STATUS_CHOICES
        context['rooms'] = Room.objects.all().order_by('room_number')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_room'] = self.request.GET.get('room', '')
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'inventory/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        return super().get_queryset().select_related('room', 'created_by')
