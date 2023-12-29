from rest_framework import serializers
from django.contrib.auth.models import Permission
from core import models


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for the group object"""

    class Meta:
        model=models.CustomGroup
        fields = ['name', 'description']

    def create(self, validated_data):
        """Create and return a group"""
        group = models.CustomGroup.objects.create(**validated_data)
        return group

    def update(self, instance, validated_data):
        """Update and return group"""
        group = super().update(instance, validated_data)

        return group
    
class PermissionSerializer(serializers.ModelSerializer):
    """Your data serializer, define your fields here."""
    class Meta:
        model=Permission
        fields = ['codename', 'name']