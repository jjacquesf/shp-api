"""
URL mappings for the evidence app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence import views

router = DefaultRouter()
router.register('', views.EvidenceViewSet)

app_name = 'evidence'

urlpatterns = [
    path('', include(router.urls)),
]