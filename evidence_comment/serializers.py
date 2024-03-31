from rest_framework import serializers
from core import models

class CreateEvidenceCommentSerializer(serializers.ModelSerializer):
    """Serializer for the evidence comment object"""
    
    class Meta:
        model= models.EvidenceComment
        fields = ['evidence', 'comments']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceComment: {self.name}'

class EvidenceCommentSerializer(serializers.ModelSerializer):
    """Serializer for the evidence comment object"""
    
    class Meta:
        model= models.EvidenceComment
        fields = ['evidence', 'user', 'comments']
        read_only_fields = ['id']

    def __str__(self):
        return f'EvidenceComment: {self.name}'