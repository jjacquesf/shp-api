"""
URL mappings for the institution app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from institution import views

router = DefaultRouter()
router.register('', views.InstitutionViewSet)

app_name = 'institution'

urlpatterns = [
    path('', include(router.urls)),
]