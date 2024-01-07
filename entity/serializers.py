from rest_framework import serializers
from core import models

class EntitySerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    
    class Meta:
        model= models.Entity
        fields = ['id', 'is_active', 'level', 'name','parent']
        read_only_fields = ['id', 'level']

    def __str__(self):
        return f'Entity: {self.name}'