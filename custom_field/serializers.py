from rest_framework import serializers
from core import models

class CustomFieldSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name')
    attribute_slug = serializers.CharField(source='attribute.slug')
    attribute_datatype = serializers.CharField(source='attribute.datatype')
    class Meta:
        model= models.CustomField
        fields = ['id', 'is_active', 'catalog', 'description', 'attribute', 'attribute_name', 'attribute_slug', 'attribute_datatype']
        read_only_fields = ['id']

class CreateCustomFieldSerializer(CustomFieldSerializer):
    attribute_name = serializers.CharField()
    attribute_slug = serializers.CharField()
    attribute_datatype = serializers.CharField()
    class Meta(CustomFieldSerializer.Meta):
        model= models.CustomField
        fields = ['id', 'is_active', 'catalog', 'description', 'attribute_name', 'attribute_slug', 'attribute_datatype']

    def create(self, validated_data):
        data = {
            "is_active": validated_data.pop("is_active", True),
            "name": validated_data.pop("attribute_name", None),
            "slug": validated_data.pop("attribute_slug", None),
            "datatype": validated_data.pop("attribute_datatype", None),
            "catalog": validated_data.pop("catalog", None),
            "description": validated_data.pop("description", None),
        }

        created = models.CustomField.create_custom_field(**data)
        serializer = CustomFieldSerializer(created)
        return serializer.data
    
class EvidenceTypeCustomFielderializer(serializers.ModelSerializer):
    """Serializer for the evidence type custom field object"""
    
    is_active = serializers.CharField(source='custom_field.is_active')
    catalog = serializers.CharField(source='custom_field.catalog')
    description = serializers.CharField(source='custom_field.description')
    attribute_name = serializers.CharField(source='custom_field.attribute.name')
    attribute_slug = serializers.CharField(source='custom_field.attribute.slug')
    attribute_datatype = serializers.CharField(source='custom_field.attribute.datatype')

    class Meta:
        model= models.EvidenceTypeCustomField
        fields = [
            'id', 
            'is_active',
            'catalog',
            'description', 
            'attribute_name',
            'attribute_slug',
            'attribute_datatype',
            'mandatory',
        ]
        read_only_fields = ['id']

class UpdateCustomFieldSerializer(CustomFieldSerializer):
    attribute_name = serializers.CharField()
    attribute_slug = serializers.CharField()
    attribute_datatype = serializers.CharField()
    class Meta(CustomFieldSerializer.Meta):
        model= models.CustomField
        fields = ['id', 'is_active', 'description']