"""
URL mappings for the dpe app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from dpe import views

router = DefaultRouter()
router.register('', views.DpeViewSet)

app_name = 'dpe'

urlpatterns = [
    path('', include(router.urls)),
]