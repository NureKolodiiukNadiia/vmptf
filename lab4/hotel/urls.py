from django.urls import path

from . import views

app_name = 'hotel'

urlpatterns = [
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
]
