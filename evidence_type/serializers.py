from rest_framework import serializers
from core import models

from custom_field.serializers import (
    EvidenceTypeCustomFieldSerializer,
    EvidenceTypeQualityControlSerializer,
)

class EvidenceTypeSerializer(serializers.ModelSerializer):
    """Serializer for the evidence type object"""
    custom_fields = serializers.SerializerMethodField()
    quality_controls = serializers.SerializerMethodField()

    class Meta:
        model= models.EvidenceType
        fields = ['id', 'is_active', 'is_owner_open', 'name', 'alias', 'attachment_required', 'level', 'parent', 'group', 'creation_status', 'description', 'custom_fields', 'quality_controls']
        read_only_fields = ['id']

    def get_custom_fields(self, obj):
        custom_fields = models.EvidenceTypeCustomField.objects.filter(type=obj)
        serializer = EvidenceTypeCustomFieldSerializer(custom_fields, many=True)
        return serializer.data
    
    def get_quality_controls(self, obj):
        quality_control = models.EvidenceTypeQualityControl.objects.filter(type=obj)
        serializer = EvidenceTypeQualityControlSerializer(quality_control, many=True)
        return serializer.data

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
