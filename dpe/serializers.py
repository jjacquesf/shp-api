from rest_framework import serializers
from core import models

class DpeSerializer(serializers.ModelSerializer):
    """Serializer for the dpe object"""
    
    class Meta:
        model= models.Dpe
        fields = ['id', 'is_active', 'name']
        read_only_fields = ['id']

    def __str__(self):
        return f'dpe: {self.name}'