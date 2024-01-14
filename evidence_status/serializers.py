from rest_framework import serializers
from core import models

class EvidenceStatusSerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    
    class Meta:
        model= models.EvidenceStatus
        fields = ['id', 'is_active', 'name', 'position', 'color', 'description', 'type', 'stage']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceStatus: {self.name}'