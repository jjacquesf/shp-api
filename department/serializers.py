from rest_framework import serializers
from core import models

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for the department object"""
    
    class Meta:
        model= models.Department
        fields = ['id', 'is_active', 'level', 'name','parent']
        read_only_fields = ['id', 'level']

    def __str__(self):
        return f'Department: {self.name}'