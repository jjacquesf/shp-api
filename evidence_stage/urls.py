"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_stage import views

app_name = 'evidence_stage'

urlpatterns = [
    path('', views.ListEvidenceStageView.as_view(), name='list')
]