"""
URL mappings for the evidence type app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from custom_field import views

router = DefaultRouter()
router.register('', views.CustomFieldViewSet)

app_name = 'customfield'

urlpatterns = [
    path('', include(router.urls)),
]