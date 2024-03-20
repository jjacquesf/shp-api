"""
URL mappings for the user API
"""
from django.urls import path

from evidence import views

app_name = 'evidence'

urlpatterns = [
    # path('token/', views.CreateTokenView.as_view(), name='token'),
    # path('me/', views.SelfManageUserView.as_view(), name='me'),
    path('create/', views.CreateEvidenceView.as_view(), name='create'),
    path('list/', views.ListEvidence.as_view(), name='list'),
    # path('<int:pk>/', views.ManageUserView.as_view(), name='detail'),
    # path('<int:pk>/group/', views.ListCreateUserGroupView.as_view(), name='group'),
]