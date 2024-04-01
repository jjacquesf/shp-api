"""
URL mappings for the evidence comments app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_finding import views

router = DefaultRouter()
router.register('', views.EvidenceFindingViewSet)

app_name = 'evidencefinding'

urlpatterns = [
    path('', include(router.urls)),
]