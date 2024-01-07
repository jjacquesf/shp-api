from rest_framework import serializers
from core import models

class InstitutionSerializer(serializers.ModelSerializer):
    """Serializer for the institution object"""
    
    class Meta:
        model= models.Institution
        fields = ['id', 'is_active', 'name']
        read_only_fields = ['id']

    def __str__(self):
        return f'Institution: {self.name}'