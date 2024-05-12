"""
URL mappings for the state organization app
"""
from django.urls import (
    path,
    include
)

from stateorg import import_views
from rest_framework.routers import DefaultRouter

from stateorg import views

router = DefaultRouter()
router.register('', views.StateOrgViewSet)

app_name = 'stateorg'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]