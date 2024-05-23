from rest_framework import serializers
from core import models

class ThemeSerializer(serializers.ModelSerializer):
    """Serializer for the theme object"""
    
    class Meta:
        model= models.Theme
        fields = ['id', 'primary', 'secondary', 'terciary', 'quaternary']
        read_only_fields = ['id']

    def __str__(self):
        return f'Theme: {self.name}'