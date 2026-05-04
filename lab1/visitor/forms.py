from django import forms
from django.core.exceptions import ValidationError
from .models import Guest, VisitLog
from inventory.models import Room


class CheckInForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'autofocus': True
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com (optional)'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890 (optional)'
        })
    )
    
    identification_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ID/Passport number (optional)'
        }),
        help_text='For security/audit purposes'
    )
    
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(status='AVAILABLE'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Leave empty for common area visits',
        empty_label='No room assignment (common area)'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes (optional)'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        
        if room:
            active_count = VisitLog.objects.filter(
                room=room,
                exit_time__isnull=True
            ).count()
            
            if active_count >= room.capacity:
                raise ValidationError(
                    f'Room {room.room_number} is at capacity ({active_count}/{room.capacity}). '
                    'Please select a different room or wait for guests to check out.'
                )
        
        return cleaned_data


class CheckOutForm(forms.Form):
    exit_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Exit notes (optional)'
        }),
        help_text='Any additional information about guest departure'
    )


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone', 'identification_number']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com (optional)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890 (optional)'
            }),
            'identification_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID/Passport number (optional)'
            })
        }
