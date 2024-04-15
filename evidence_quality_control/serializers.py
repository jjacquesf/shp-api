from quality_control.serializers import QualityControlSerializer
from rest_framework import serializers
from core import models
from user.serializers import BaseUserSerializer
from django.contrib.auth import (
    get_user_model,
)

class CreateEvidenceQualityControlSerializer(serializers.Serializer):
    """Serializer for user creation."""
    user = serializers.IntegerField(required=False)
    evidence = serializers.IntegerField(required=True)
    quality_control = serializers.IntegerField(required=True)
    comments = serializers.CharField(required=True)

    def create(self, validated_data):
        quality_control = models.QualityControl.objects.get(id=validated_data.get('quality_control'))
        evidence = models.Evidence.objects.get(id=validated_data.get('evidence'))
        user = get_user_model().objects.get(id=validated_data.get('user'))
        comments = validated_data.get('comments')
        
        data = {
            "quality_control": quality_control,
            "evidence": evidence,
            "user": user,
            "comments": comments,
            "status": "PEN"
        }

        instance = models.EvidenceQualityControl.objects.create(**data)

        s = EvidenceQualityControlSerializer(instance)
        return s.data


class EvidenceQualityControlSerializer(serializers.ModelSerializer):
    """Serializer for the evidence comment object"""
    user = BaseUserSerializer()
    # evidence = BaseUserSerializer()
    quality_control = QualityControlSerializer()

    class Meta:
        model= models.EvidenceQualityControl
        fields = ['status', 'user', 'evidence', 'quality_control', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def __str__(self):
        return f'EvidenceQualityControl: {self.name}'
    