"""
URL mappings for the evidence comments app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_comment import views

router = DefaultRouter()
router.register('', views.EvidenceCommentViewSet)

app_name = 'evidencecomment'

urlpatterns = [
    path('', include(router.urls)),
]