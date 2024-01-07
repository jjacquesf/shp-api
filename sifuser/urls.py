"""
URL mappings for theSIF userapp
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from sifuser import views

router = DefaultRouter()
router.register('sifusers', views.SifUserViewSet)

app_name = 'sifuser'

urlpatterns = [
    path('', include(router.urls)),
]