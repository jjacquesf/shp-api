"""
URL mappings for the department app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from department import views, import_views

router = DefaultRouter()
router.register('', views.DepartmentViewSet)

app_name = 'department'

urlpatterns = [
    path('import/<slug:filename>/', import_views.ImportView.as_view(), name='import'),
    path('', include(router.urls)),

]