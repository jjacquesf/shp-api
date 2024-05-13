"""
URL mappings for the municipality app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from municipality import views, import_views

router = DefaultRouter()
router.register('', views.MunicipalityViewSet)

app_name = 'municipality'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]