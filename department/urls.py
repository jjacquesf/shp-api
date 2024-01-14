"""
URL mappings for the department app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from department import views

router = DefaultRouter()
router.register('', views.DepartmentViewSet)

app_name = 'department'

urlpatterns = [
    path('', include(router.urls)),
]