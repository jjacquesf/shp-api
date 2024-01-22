"""
URL mappings for the evidence type app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_type import views

router = DefaultRouter()
router.register('', views.EvidenceTypeViewSet)

app_name = 'evidencetype'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/custom-fields/', views.ListCreateCustomFieldView.as_view(), name='custom-fields'),
    path('<int:pk>/custom-fields/<int:cf_id>', views.DeleteCustomFieldView.as_view(), name='custom-fields-delete'),
]