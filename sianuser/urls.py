"""
URL mappings for the SIAN userapp
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from sianuser import views

router = DefaultRouter()
router.register('', views.SianUserViewSet)

app_name = 'sianuser'

urlpatterns = [
    path('', include(router.urls)),
]