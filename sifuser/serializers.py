from rest_framework import serializers
from core import models

class SifUserSerializer(serializers.ModelSerializer):
    """Serializer for theSIF userobject"""
    
    class Meta:
        model= models.SifUser
        fields = ['id', 'is_active', 'name','stateorg']
        read_only_fields = ['id']

    def __str__(self):
        return f'SifUser: {self.name}'