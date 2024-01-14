from rest_framework import serializers
from core import models

class EvidenceStageSerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    
    class Meta:
        model= models.EvidenceStage
        fields = ['id', 'is_active', 'name', 'position','description']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceStage: {self.name}'