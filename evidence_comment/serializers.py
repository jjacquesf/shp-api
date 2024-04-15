from rest_framework import serializers
from core import models
from user.serializers import BaseUserSerializer
from django.contrib.auth import (
    get_user_model,
)
class CreateEvidenceCommentSerializer(serializers.Serializer):
    """Serializer for the evidence comment object"""

    evidence = serializers.CharField(required=True)
    comments = serializers.CharField(required=True)
    user = serializers.IntegerField(required=False)
    
    def create(self, validated_data):
        evidence = models.Evidence.objects.get(id=validated_data.get('evidence'))
        user = get_user_model().objects.get(id=validated_data.get('user'))
        comments = validated_data.get('comments')
        
        data = {
            "evidence": evidence,
            "user": user,
            "comments": comments,
        }

        instance = models.EvidenceComment.objects.create(**data)

        s = EvidenceCommentSerializer(instance)
        return s.data

class EvidenceCommentSerializer(serializers.ModelSerializer):
    """Serializer for the evidence comment object"""
    user = BaseUserSerializer()

    class Meta:
        model= models.EvidenceComment
        fields = ['evidence', 'user', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at']

    def __str__(self):
        return f'EvidenceComment: {self.name}'
    