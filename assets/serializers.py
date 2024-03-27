from rest_framework import serializers
from core import models

class CreateFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UploadedFile
        fields = ('file', 'uploaded_on')

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UploadedFile
        fields = ('id','file', 'owner', 'uploaded_on',)