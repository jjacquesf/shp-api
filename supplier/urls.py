"""
URL mappings for the supplier app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from supplier import views, import_views

router = DefaultRouter()
router.register('', views.SupplierViewSet)

app_name = 'supplier'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),
]