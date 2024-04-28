"""
URL mappings for the user API
"""
from django.urls import path

from report import report_views
from report import analytics_views

app_name = 'report'

urlpatterns = [
    # path('custom-field-options/<int:pk>/', views.CustomFieldOptions.as_view(), name='custom-field-options'),
    path('evidences/', report_views.EvidenceReportView.as_view(), name='evidences'),
    path('evidemce-analytics/', analytics_views.EvidenceAnalyticsView.as_view(), name='evidemce-analytics'),
    # path('me/', views.SelfManageUserView.as_view(), name='me'),
    # path('create/', views.CreateUserView.as_view(), name='create'),
    # path('list/', views.ListUserView.as_view(), name='list'),
    # path('<int:pk>/', views.ManageUserView.as_view(), name='detail'),
    # path('<int:pk>/group/', views.ListCreateUserGroupView.as_view(), name='group'),
]