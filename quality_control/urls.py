"""
URL mappings for the evidence comments app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from quality_control import views

router = DefaultRouter()
router.register('', views.QualityControlViewSet)

app_name = 'qualitycontrol'

urlpatterns = [
    path('', include(router.urls)),
]