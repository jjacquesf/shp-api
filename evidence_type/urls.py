"""
URL mappings for the evidence type app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_type import views

router = DefaultRouter()
router.register('', views.EvidenceTypeViewSet)

app_name = 'evidencetype'

urlpatterns = [
    path('', include(router.urls)),
]