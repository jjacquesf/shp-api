"""
URL mappings for the dpe app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from dpe import views, import_views

router = DefaultRouter()
router.register('', views.DpeViewSet)

app_name = 'dpe'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]