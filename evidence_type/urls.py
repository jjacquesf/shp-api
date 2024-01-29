"""
URL mappings for the evidence type app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from evidence_type import views

main_router = DefaultRouter()
main_router.register('', views.EvidenceTypeViewSet)

app_name = 'evidencetype'

urlpatterns = [
    path('', include(main_router.urls)),
    path('<int:pk>/custom-fields/', views.ListCreateCustomFieldView.as_view(), name='custom-fields'),
    path('<int:pk>/custom-fields/<int:cf_id>', views.PatchDeleteCustomFieldView.as_view(), name='custom-fields-detail'),
]