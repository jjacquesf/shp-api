"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_quality_control import views

router = DefaultRouter()
router.register('', views.EvidenceQualityControlViewSet)

app_name = 'evidencequalitycontrol'

urlpatterns = [
    path('', include(router.urls)),
]