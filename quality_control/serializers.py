from rest_framework import serializers
from core import models

class QualityControlSerializer(serializers.ModelSerializer):
    """Serializer for the quality control object"""
    
    class Meta:
        model= models.QualityControl
        fields = ['id', 'is_active', 'type', 'name']
        read_only_fields = ['id']

    def __str__(self):
        return f'QualityControl: {self.name}'