"""
URL mappings for the user API
"""
from django.urls import path

from user import views, auth_views

app_name = 'user'

urlpatterns = [
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('reset-password/', auth_views.ResetPasswordView.as_view(), name='token'),
    path('me/', views.SelfManageUserView.as_view(), name='me'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('list/', views.ListUserView.as_view(), name='list'),
    path('<int:pk>/', views.ManageUserView.as_view(), name='detail'),
    path('<int:pk>/group/', views.ListCreateUserGroupView.as_view(), name='group'),
]