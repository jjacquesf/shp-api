from rest_framework import serializers
from core import models

class MunicipalitySerializer(serializers.ModelSerializer):
    """Serializer for the municipality object"""
    
    class Meta:
        model= models.Municipality
        fields = ['id', 'is_active', 'name']
        read_only_fields = ['id']

    def __str__(self):
        return f'Municipality: {self.name}'