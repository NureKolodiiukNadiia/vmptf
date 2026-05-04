from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DetailView

from .models import Guest, VisitLog
from .forms import CheckInForm, CheckOutForm
from .services import ConciergeService


class CheckInView(LoginRequiredMixin, FormView):
    form_class = CheckInForm
    template_name = 'visitor/checkin.html'
    success_url = reverse_lazy('visitor:active_visits')
    
    def form_valid(self, form):
        try:
            guest, created = ConciergeService.create_or_get_guest(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data.get('email', ''),
                phone=form.cleaned_data.get('phone', ''),
                identification_number=form.cleaned_data.get('identification_number', '')
            )
            
            visit_log = ConciergeService.record_entry(
                guest=guest,
                room=form.cleaned_data.get('room'),
                processed_by=self.request.user,
                notes=form.cleaned_data.get('notes', '')
            )
            
            room_info = f" to room {visit_log.room.room_number}" if visit_log.room else ""
            messages.success(
                self.request,
                f'✓ {guest.full_name} checked in successfully{room_info}'
            )
            
            return redirect(self.success_url)
            
        except ValueError as e:
            messages.error(self.request, f'Check-in failed: {e}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_visits_count'] = VisitLog.objects.filter(
            exit_time__isnull=True
        ).count()
        return context


class CheckOutView(LoginRequiredMixin, FormView):
    form_class = CheckOutForm
    template_name = 'visitor/checkout.html'
    success_url = reverse_lazy('visitor:active_visits')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visit_log = get_object_or_404(
            VisitLog.objects.select_related('guest', 'room'),
            pk=self.kwargs['visit_log_id']
        )
        context['visit_log'] = visit_log
        return context
    
    def form_valid(self, form):
        visit_log = get_object_or_404(VisitLog, pk=self.kwargs['visit_log_id'])
        
        try:
            updated_log = ConciergeService.record_exit(
                visit_log=visit_log,
                exit_notes=form.cleaned_data.get('exit_notes', '')
            )
            
            room_info = f" from room {updated_log.room.room_number}" if updated_log.room else ""
            duration = updated_log.duration
            duration_str = f" (Duration: {duration})" if duration else ""
            
            messages.success(
                self.request,
                f'✓ {updated_log.guest.full_name} checked out successfully{room_info}{duration_str}'
            )
            
            return redirect(self.success_url)
            
        except ValueError as e:
            messages.error(self.request, f'Check-out failed: {e}')
            return redirect('visitor:active_visits')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below')
        return super().form_invalid(form)


class ActiveVisitsView(LoginRequiredMixin, ListView):
    template_name = 'visitor/active_visits.html'
    context_object_name = 'visits'
    
    def get_queryset(self):
        return ConciergeService.get_active_visits().select_related(
            'guest', 'room', 'processed_by'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visits = context['visits']
        
        context['total_guests'] = visits.count()
        context['guests_with_rooms'] = visits.filter(room__isnull=False).count()
        context['guests_common_area'] = visits.filter(room__isnull=True).count()
        
        return context


class VisitHistoryView(LoginRequiredMixin, ListView):
    model = VisitLog
    template_name = 'visitor/visit_history.html'
    context_object_name = 'visits'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = VisitLog.objects.select_related('guest', 'room', 'processed_by')
        guest_id = self.request.GET.get('guest')
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)
        room_id = self.request.GET.get('room')
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(exit_time__isnull=True)
        elif status == 'completed':
            queryset = queryset.filter(exit_time__isnull=False)
        
        days = int(self.request.GET.get('days', 30))
        queryset = ConciergeService.get_visit_history(days=days)
        
        return queryset.order_by('-entry_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guests'] = Guest.objects.all().order_by('last_name', 'first_name')
        
        from inventory.models import Room
        context['rooms'] = Room.objects.all().order_by('room_number')
        
        context['current_guest'] = self.request.GET.get('guest', '')
        context['current_room'] = self.request.GET.get('room', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_days'] = self.request.GET.get('days', '30')
        
        return context


class GuestListView(LoginRequiredMixin, ListView):
    model = Guest
    template_name = 'visitor/guest_list.html'
    context_object_name = 'guests'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search', '')
        return context


class VisitDetailView(LoginRequiredMixin, DetailView):
    model = VisitLog
    template_name = 'visitor/visit_detail.html'
    context_object_name = 'visit'
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'guest', 'room', 'processed_by'
        )
