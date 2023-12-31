"""
Serializer for the user API view
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

from rest_framework import serializers
from core import models

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model=get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Creare and return a user with encrypted password"""
        user = get_user_model().objects.create_user(**validated_data)
        
        # default_group = models.CustomGroup.objects.get(name='admin')
        # default_group.user_set.add(user)

        return user

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and autenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to autenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
    
class IntegerListField(serializers.ListField):
    child = serializers.IntegerField(min_value=1)
class UpdateUserGroupSerializer(serializers.Serializer):
    """Serializer for user group update."""
    groups = IntegerListField()