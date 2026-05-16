from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Booking, Client, Hotel, Room, Service
from .services import BookingService


class BookingForm(forms.ModelForm):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Booking
        fields = ['client', 'room', 'services', 'check_in_date', 'check_out_date', 'status']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-control'}),
            'services': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(status='AVAILABLE').select_related('hotel')
        self.fields['client'].queryset = Client.objects.all().order_by('last_name', 'first_name')
        self.fields['services'].queryset = Service.objects.select_related('hotel').order_by('hotel__name', 'name')
        self.fields['services'].required = False
        self.fields['services'].help_text = 'Hold Ctrl (Cmd on Mac) to select multiple services.'
        self.fields['services'].widget.attrs.update({'size': 8})

    def clean_check_in_date(self):
        check_in = self.cleaned_data.get('check_in_date')
        if check_in and check_in < timezone.now().date():
            raise ValidationError('Check-in date cannot be in the past')
        return check_in

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        services = cleaned_data.get('services')

        if check_in and check_out and check_out <= check_in:
            raise ValidationError('Check-out date must be after check-in date')

        if room and check_in and check_out:
            exclude_id = self.instance.pk if self.instance.pk else None
            if not BookingService.check_room_availability(room, check_in, check_out, exclude_booking_id=exclude_id):
                raise ValidationError(
                    f'Room {room.room_number} is not available for the selected dates.'
                )

        if room and services:
            invalid_services = [service.name for service in services if service.hotel_id != room.hotel_id]
            if invalid_services:
                raise ValidationError(
                    f"Selected services must belong to hotel '{room.hotel.name}'. "
                    f'Invalid: {", ".join(invalid_services)}'
                )

        return cleaned_data


class AvailabilityForm(forms.Form):
    hotel = forms.ModelChoiceField(
        queryset=Hotel.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    check_in_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    check_out_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    min_capacity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('check_in_date')
        end = cleaned.get('check_out_date')
        if start and end and end <= start:
            raise ValidationError('Check-out date must be after check-in date')
        return cleaned
