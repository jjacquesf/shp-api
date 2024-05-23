"""
URL mappings for the theme app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from theme import views, colors_view

router = DefaultRouter()
router.register('', views.ThemeViewSet)

app_name = 'theme'

urlpatterns = [
    path('colors/', colors_view.ColorsView.as_view(), name='colors'),
    path('', include(router.urls)),
]