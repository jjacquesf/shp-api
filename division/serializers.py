from rest_framework import serializers
from core import models

class DivisionSerializer(serializers.ModelSerializer):
    """Serializer for the division object"""
    
    class Meta:
        model= models.Division
        fields = ['id', 'is_active', 'name']
        read_only_fields = ['id']

    def __str__(self):
        return f'Division: {self.name}'