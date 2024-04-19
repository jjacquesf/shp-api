"""
URL mappings for the division app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from division import views

router = DefaultRouter()
router.register('', views.DivisionViewSet)

app_name = 'division'

urlpatterns = [
    path('', include(router.urls)),
]