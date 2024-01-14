from rest_framework import serializers
from core import models

class EvidenceTypeSerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    
    class Meta:
        model= models.EvidenceType
        fields = ['id', 'is_active', 'name', 'alias','description']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceType: {self.name}'