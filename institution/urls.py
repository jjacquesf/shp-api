"""
URL mappings for the institution app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from institution import views, import_views

router = DefaultRouter()
router.register('', views.InstitutionViewSet)

app_name = 'institution'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]