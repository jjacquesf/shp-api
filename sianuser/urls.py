"""
URL mappings for the SIAN userapp
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from sianuser import import_views, views

router = DefaultRouter()
router.register('', views.SianUserViewSet)

app_name = 'sianuser'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]