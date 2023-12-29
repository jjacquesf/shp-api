from rest_framework import serializers
from django.contrib.auth.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for the permission object"""

    class Meta:
        model=Permission
        fields = ['codename', 'name']