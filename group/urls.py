"""
URL mappings for the user API
"""
from django.urls import path

from group import views

app_name = 'group'

urlpatterns = [
    path('create/', views.CreateGroupView.as_view(), name='create'),
    path('list/', views.ListGroupView.as_view(), name='list'),
]