from rest_framework import serializers
from core import models

class StateOrgSerializer(serializers.ModelSerializer):
    """Serializer for the state organization object"""
    
    class Meta:
        model= models.StateOrg
        fields = ['id', 'is_active', 'level', 'name','parent']
        read_only_fields = ['id', 'level']

    def __str__(self):
        return f'StateOrg: {self.name}'