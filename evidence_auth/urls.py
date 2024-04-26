"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_auth import views

router = DefaultRouter()
router.register('', views.EvidenceAuthViewSet)

app_name = 'evidenceauth'

urlpatterns = [
    path('', include(router.urls)),
]