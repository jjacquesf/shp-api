from rest_framework import serializers
from core import models

class EvidenceTypeSerializer(serializers.ModelSerializer):
    """Serializer for the evidence type object"""
    
    class Meta:
        model= models.EvidenceType
        fields = ['id', 'is_active', 'name', 'alias', 'attachment_required', 'level', 'parent', 'group', 'description']
        read_only_fields = ['id']

class AddEvidenceTypeCustomFieldSerializer(serializers.Serializer):
    """Serializer for user group add."""
    is_active = serializers.BooleanField(default=True)
    custom_field = serializers.IntegerField(min_value=1)
    mandatory = serializers.BooleanField(default=True)
    group = serializers.CharField(max_length=64)

class UpdateEvidenceTypeCustomFieldSerializer(serializers.Serializer):
    """Serializer for user group update."""
    is_active = serializers.BooleanField(default=True)
    mandatory = serializers.BooleanField(default=True)
    group = serializers.CharField(max_length=64)

class QualityControlSerializer(serializers.ModelSerializer):
    """Serializer for the evidence type object"""
    
    class Meta:
        model= models.QualityControl
        fields = ['id', 'is_active', 'name']
        read_only_fields = ['id']

class AddPatchQualityControlSerializer(QualityControlSerializer):
    """Serializer for the evidence type object"""
    
    class Meta(QualityControlSerializer.Meta):
        fields = ['id', 'is_active', 'name']


class AddEvidenceTypeQualityControlSerializer(serializers.Serializer):
    """Serializer for user group add."""
    is_active = serializers.BooleanField(default=True)
    quality_control = serializers.IntegerField(min_value=1)
class UpdateEvidenceTypeQualityControlSerializer(serializers.Serializer):
    """Serializer for user group update."""
    is_active = serializers.BooleanField(default=True)
    # quality_control = serializers.IntegerField(min_value=1)
