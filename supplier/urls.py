"""
URL mappings for the supplier app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from supplier import views

router = DefaultRouter()
router.register('', views.SupplierViewSet)

app_name = 'supplier'

urlpatterns = [
    path('', include(router.urls)),
]