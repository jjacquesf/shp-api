"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_signature import views

router = DefaultRouter()
router.register('', views.EvidenceSignatureViewSet)

app_name = 'evidencesignature'

urlpatterns = [
    path('', include(router.urls)),
]