"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_status import views

router = DefaultRouter()
router.register('evidence_statuses', views.EvidenceStatusViewSet)

app_name = 'evidencestatus'

urlpatterns = [
    path('', include(router.urls)),
]