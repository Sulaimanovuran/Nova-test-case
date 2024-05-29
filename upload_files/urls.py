from django.urls import path
from .views import create_file, create_upload_file

urlpatterns = [
    path('drive/', create_file, name='drive'),
    path('drive/v2/', create_upload_file, name='drive_v2')
]