from rest_framework import serializers
from core import models

class EvidenceTypeSerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    
    class Meta:
        model= models.EvidenceType
        fields = ['id', 'is_active', 'name', 'alias', 'attachment_required', 'level', 'parent', 'group', 'description']
        read_only_fields = ['id']

class UpdateEvidenceTypeCustomFieldSerializer(serializers.Serializer):
    """Serializer for user group update."""
    custom_field = serializers.IntegerField(min_value=1)
    mandatory = serializers.BooleanField(default=True)