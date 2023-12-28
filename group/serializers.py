from rest_framework import serializers
from core import models


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for the group object"""

    class Meta:
        model=models.CustomGroup
        fields = ['name', 'description']