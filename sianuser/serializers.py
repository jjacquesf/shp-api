from rest_framework import serializers
from core import models

class SianUserSerializer(serializers.ModelSerializer):
    """Serializer for the SIAN userobject"""
    
    class Meta:
        model= models.SianUser
        fields = ['id', 'is_active', 'name','stateorg']
        read_only_fields = ['id']

    def __str__(self):
        return f'SianUser: {self.name}'