"""
URL mappings for the entity app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from entity import import_views, views

router = DefaultRouter()
router.register('', views.EntityViewSet)

app_name = 'entity'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]