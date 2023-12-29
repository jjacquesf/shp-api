"""
URL mappings for the user API
"""
from django.urls import path

from group import views

app_name = 'group'

urlpatterns = [
    path('', views.ListCreateGroupView.as_view(), name='list_create'),
    path('<int:pk>/', views.ManageGroupView.as_view(), name='manage'),
    path('<int:pk>/permission/', views.ListCreateGroupPermissionView.as_view(), name='permission'),
]