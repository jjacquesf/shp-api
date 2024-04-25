from evidence.serializers import EvidenceSerializer
from quality_control.serializers import QualityControlSerializer
from rest_framework import serializers
from core import models
from user.serializers import BaseUserSerializer
from django.contrib.auth import (
    get_user_model,
)

class CreateNotificationSerializer(serializers.Serializer):
    """Serializer for user creation."""
    user = serializers.IntegerField(required=False)
    evidence = serializers.IntegerField(required=True)
    content = serializers.CharField(required=True)

    def create(self, validated_data):
        evidence = models.Evidence.objects.get(id=validated_data.get('evidence'))
        user = get_user_model().objects.get(id=validated_data.get('user'))
        content = validated_data.get('content')
        
        data = {
            "evidence": evidence,
            "user": user,
            "content": content,
            "opened": False
        }

        instance = models.Notification.objects.create(**data)

        s = NotificationSerializer(instance)
        return s.data


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for the evidence comment object"""
    user = BaseUserSerializer()
    evidence = EvidenceSerializer()

    class Meta:
        model= models.Notification
        fields = ['id', 'opened', 'user', 'evidence', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def __str__(self):
        return f'Notification: {self.id}'
    

class UpdateNotificationSerializer(serializers.ModelSerializer):
    """Serializer for the evidence comment object"""
    class Meta:
        model= models.Notification
        fields = ['id', 'opened']

    def __str__(self):
        return f'UpdateNotificationSerializer: {self.id}'
    