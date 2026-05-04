from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Room, Booking
from .services import BookingService


class BookingForm(forms.ModelForm):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Guest check-in date'
    )
    
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Guest check-out date'
    )
    
    class Meta:
        model = Booking
        fields = ['room', 'guest_name', 'guest_email', 'guest_phone', 
                 'check_in_date', 'check_out_date']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com (optional)'
            }),
            'guest_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890 (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(status='AVAILABLE')
    
    def clean_check_in_date(self):
        check_in = self.cleaned_data.get('check_in_date')
        if check_in and check_in < timezone.now().date():
            raise ValidationError('Check-in date cannot be in the past')
        return check_in
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        room = cleaned_data.get('room')
        
        if check_in and check_out:
            if check_out < check_in:
                raise ValidationError('Check-out date must be after check-in date')
        
        if room and check_in and check_out:
            exclude_id = self.instance.pk if self.instance.pk else None
            
            if not BookingService.check_room_availability(
                room=room,
                check_in_date=check_in,
                check_out_date=check_out,
                exclude_booking_id=exclude_id
            ):
                raise ValidationError(
                    f'Room {room.room_number} is not available for the selected dates. '
                    'Please choose different dates or another room.'
                )
        
        return cleaned_data


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'capacity', 'status', 'description']
        widgets = {
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 101, A-205'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Room description (optional)'
            })
        }
