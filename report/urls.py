"""
URL mappings for the user API
"""
from django.urls import path

from report import views

app_name = 'report'

urlpatterns = [
    path('demo/', views.ReportView.as_view(), name='demo'),
    # path('me/', views.SelfManageUserView.as_view(), name='me'),
    # path('create/', views.CreateUserView.as_view(), name='create'),
    # path('list/', views.ListUserView.as_view(), name='list'),
    # path('<int:pk>/', views.ManageUserView.as_view(), name='detail'),
    # path('<int:pk>/group/', views.ListCreateUserGroupView.as_view(), name='group'),
]