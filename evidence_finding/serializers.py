from rest_framework import serializers
from core import models

class EvidenceFindingSerializer(serializers.ModelSerializer):
    """Serializer for the evidence finding object"""
    
    class Meta:
        model= models.EvidenceFinding
        fields = ['id', 'status', 'evidence', 'qc', 'comments']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceFinding: {self.name}'