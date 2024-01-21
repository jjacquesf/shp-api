from rest_framework import serializers
from core import models

from core.serializers import (
    IntegerListField,
)

class EvidenceTypeSerializer(serializers.ModelSerializer):
    """Serializer for the entity object"""
    
    class Meta:
        model= models.EvidenceType
        fields = ['id', 'is_active', 'name', 'alias', 'attachment_required', 'level', 'parent', 'group', 'description']
        read_only_fields = ['id']
    

class UpdateCustomFieldSerializer(serializers.Serializer):
    """Serializer for user group update."""
    custom_fields = IntegerListField()
    
class CustomFieldSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name')
    attribute_slug = serializers.CharField(source='attribute.slug')
    attribute_datatype = serializers.CharField(source='attribute.datatype')
    class Meta:
        model= models.CustomField
        fields = ['id', 'is_active', 'description', 'attribute', 'attribute_name', 'attribute_slug', 'attribute_datatype']
        read_only_fields = ['id']