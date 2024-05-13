"""
URL mappings for theSIF userapp
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from sifuser import views, import_views

router = DefaultRouter()
router.register('', views.SifUserViewSet)

app_name = 'sifuser'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]