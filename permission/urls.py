"""
URL mappings for the user API
"""
from django.urls import path

from permission import views

app_name = 'permission'

urlpatterns = [
    path('', views.ListPermissionView.as_view(), name='list'),
]