from django.db import transaction
from django.utils import timezone
from .models import Guest, VisitLog


class ConciergeService:
    @staticmethod
    @transaction.atomic
    def create_or_get_guest(first_name, last_name, email='', phone='', 
                           identification_number=''):
        guest, created = Guest.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={
                'email': email,
                'phone': phone,
                'identification_number': identification_number
            }
        )
        
        if not created:
            updated = False
            if email and guest.email != email:
                guest.email = email
                updated = True
            if phone and guest.phone != phone:
                guest.phone = phone
                updated = True
            if identification_number and guest.identification_number != identification_number:
                guest.identification_number = identification_number
                updated = True
            
            if updated:
                guest.save()
        
        return guest, created
    
    @staticmethod
    @transaction.atomic
    def record_entry(guest, room=None, processed_by=None, notes=''):
        if room:
            active_visits_count = VisitLog.objects.filter(
                room=room,
                exit_time__isnull=True
            ).count()
            
            if active_visits_count >= room.capacity:
                raise ValueError(
                    f'Room {room.room_number} is at capacity '
                    f'({active_visits_count}/{room.capacity}). Cannot check in more guests.'
                )
        
        visit_log = VisitLog.objects.create(
            guest=guest,
            room=room,
            entry_time=timezone.now(),
            processed_by=processed_by,
            notes=notes
        )
        
        return visit_log
    
    @staticmethod
    @transaction.atomic
    def record_exit(visit_log, exit_notes=''):
        if visit_log.exit_time is not None:
            raise ValueError(
                f'Visit log {visit_log.id} already has exit time recorded: '
                f'{visit_log.exit_time}'
            )
        
        visit_log.exit_time = timezone.now()
        if exit_notes:
            if visit_log.notes:
                visit_log.notes += f'\n\nExit: {exit_notes}'
            else:
                visit_log.notes = f'Exit: {exit_notes}'
        
        visit_log.save(update_fields=['exit_time', 'notes'])
        
        return visit_log
    
    @staticmethod
    def get_active_visits(room=None):
        queryset = VisitLog.objects.filter(
            exit_time__isnull=True
        ).select_related('guest', 'room', 'processed_by')
        
        if room:
            queryset = queryset.filter(room=room)
        
        return queryset.order_by('entry_time')
    
    @staticmethod
    def get_visit_history(guest=None, room=None, days=30):
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        queryset = VisitLog.objects.filter(
            entry_time__gte=cutoff_date
        ).select_related('guest', 'room', 'processed_by')
        
        if guest:
            queryset = queryset.filter(guest=guest)
        
        if room:
            queryset = queryset.filter(room=room)
        
        return queryset.order_by('-entry_time')
