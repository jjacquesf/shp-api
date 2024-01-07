"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from entity import views

router = DefaultRouter()
router.register('entities', views.EntityViewSet)

app_name = 'entity'

urlpatterns = [
    path('', include(router.urls)),
]