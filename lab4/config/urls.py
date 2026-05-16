"""
Project Root URL Configuration
"""

from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/hotel/rooms/', permanent=False), name='root'),
    path('inventory/', include('hotel.urls')),
]
