from evidence_group.serializers import EvidenceGroupSerializer
from evidence_stage.serializers import EvidenceStageSerializer
from rest_framework import serializers
from core import models

class SaveEvidenceStatusSerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    class Meta:
        model= models.EvidenceStatus
        fields = ['id', 'is_active', 'name', 'position', 'color', 'description', 'group', 'stage']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceStatus: {self.name}'

class EvidenceStatusSerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    group = EvidenceGroupSerializer()
    stage = EvidenceStageSerializer()
    class Meta:
        model= models.EvidenceStatus
        fields = ['id', 'is_active', 'name', 'position', 'color', 'description', 'group', 'stage']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceStatus: {self.name}'