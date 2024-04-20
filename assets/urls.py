from django.urls import path
from assets import views

app_name = 'assets'

urlpatterns = [
    path('upload-file/', views.FileUploadAPIView.as_view(), name='upload-file'),
    path('download-file/<int:pk>', views.FileDownloadAPIView.as_view(), name='download-file'),
]