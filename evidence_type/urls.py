"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_type import views

app_name = 'evidence_type'

urlpatterns = [
    path('', views.ListEvidenceTypeView.as_view(), name='list')
]