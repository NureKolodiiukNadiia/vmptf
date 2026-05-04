from django.urls import path
from . import views

app_name = 'visitor'

urlpatterns = [
    # Check-in/Check-out URLs
    path('checkin/', views.CheckInView.as_view(), name='checkin'),
    path('checkout/<int:visit_log_id>/', views.CheckOutView.as_view(), name='checkout'),
    
    # Visit tracking URLs
    path('active/', views.ActiveVisitsView.as_view(), name='active_visits'),
    path('history/', views.VisitHistoryView.as_view(), name='visit_history'),
    path('visits/<int:pk>/', views.VisitDetailView.as_view(), name='visit_detail'),
    
    # Guest management URLs
    path('guests/', views.GuestListView.as_view(), name='guest_list'),
]
