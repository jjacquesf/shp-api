"""
URL mappings for the state organization app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from stateorg import views

router = DefaultRouter()
router.register('', views.StateOrgViewSet)

app_name = 'stateorg'

urlpatterns = [
    path('', include(router.urls)),
]