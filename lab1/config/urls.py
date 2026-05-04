"""
Project Root URL Configuration
"""

from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/users/login/', permanent=False), name='root'),
    path('users/', include('users.urls')),
    path('inventory/', include('inventory.urls')),
    path('visitor/', include('visitor.urls')),
]