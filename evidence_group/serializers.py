from rest_framework import serializers
from core import models

class EvidenceGroupSerializer(serializers.ModelSerializer):
    """Serializer for the evidence group object"""
    
    class Meta:
        model= models.EvidenceGroup
        fields = ['id', 'is_active', 'name', 'alias', 'description']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceGroup: {self.name}'