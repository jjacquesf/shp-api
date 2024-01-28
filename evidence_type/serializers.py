from rest_framework import serializers
from core import models

class EvidenceTypeSerializer(serializers.ModelSerializer):
    """Serializer for the evidence type object"""
    
    class Meta:
        model= models.EvidenceType
        fields = ['id', 'is_active', 'name', 'alias', 'attachment_required', 'level', 'parent', 'group', 'description']
        read_only_fields = ['id']

class UpdateEvidenceTypeCustomFieldSerializer(serializers.Serializer):
    """Serializer for user group update."""
    custom_field = serializers.IntegerField(min_value=1)
    mandatory = serializers.BooleanField(default=True)
    group = serializers.CharField(min_length=64)

class EvidenceTypeQualityControlSerializer(serializers.ModelSerializer):
    """Serializer for the evidence type quality control object"""
    
    class Meta:
        model= models.EvidenceTypeQualityControl
        fields = ['id', 'is_active', 'type', 'name']
        read_only_fields = ['id']
