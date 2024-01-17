"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_group import views

app_name = 'evidence_group'

urlpatterns = [
    path('', views.ListEvidenceGroupView.as_view(), name='list')
]