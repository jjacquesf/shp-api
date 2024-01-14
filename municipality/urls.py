"""
URL mappings for the municipality app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from municipality import views

router = DefaultRouter()
router.register('', views.MunicipalityViewSet)

app_name = 'municipality'

urlpatterns = [
    path('', include(router.urls)),
]