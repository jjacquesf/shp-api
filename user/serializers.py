"""
Serializer for the user API view
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _
from division.serializers import DivisionSerializer
from group.serializers import StringListField

from rest_framework import serializers
from core import models

from core.serializers import (
    IntegerListField,
)

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
    
class UpdateUserGroupSerializer(serializers.Serializer):
    """Serializer for user group update."""
    groups = IntegerListField()

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the profile object"""
    class Meta:
        model=models.Profile
        fields = ['user', 'job_position', 'division']

    def create(self, validated_data):
        """Create and return profile"""
        profile = models.Profile.objects.create(**validated_data)
        return profile

    def update(self, instance, validated_data):
        """Update and return profile"""

        profile = super().update(instance, validated_data)
        return profile


class SaveUserProfileSerializer(serializers.Serializer):
    """Serializer for user creation."""
    id = serializers.EmailField(required=False)
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=False, allow_blank=True, min_length=5, max_length=255)
    job_position = serializers.CharField(required=True, max_length=255)
    division = serializers.IntegerField(required=True)

    def create(self, validated_data):
        user_data = {
            "email": validated_data.get("email"),
            "name": validated_data.get("name"),
            "password": validated_data.pop("password", None),
        }

        user = get_user_model().objects.create_user(**user_data)
        division = models.Division.objects.get(id=validated_data.get('division'))

        profile_data = {
            "user": user.id,
            "job_position": validated_data.get("job_position"),
            "division": division.id
        }

        profile_serializer = ProfileSerializer(data=profile_data)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        validated_data.pop("password", None)

        user.refresh_from_db()
        profile = models.Profile.objects.get(user=user)

        serializer = UserProfileSerializer({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "job_position": profile.job_position,
            "division": profile.division
        })
        return serializer.data

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        job_position = validated_data.pop('job_position', None)
        division = validated_data.pop('division', None)

        if password:
            instance.set_password(password)
            instance.save()

        get_user_model().objects.filter(id=instance.pk).update(**validated_data)

        instance.refresh_from_db()

        profile_data = {}
        
        if(job_position != None):
            profile_data.update({"job_position": job_position})

        if(division != None):
            profile_data.update({"division": division})

        models.Profile.objects.filter(user=instance).update(**profile_data)

        serializer = serialize_user_profile(instance)

        return serializer.data



class UserProfileSerializer(serializers.Serializer):
    """Serializer for user creation."""
    id = serializers.EmailField(required=False)
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=False, allow_blank=True, min_length=5, max_length=255)
    job_position = serializers.CharField(required=True, max_length=255)
    division = DivisionSerializer()
class FullUserProfileSerializer(serializers.Serializer):
    """Serializer for user creation."""
    id = serializers.EmailField(required=False)
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=False, allow_blank=True, min_length=5, max_length=255)
    job_position = serializers.CharField(required=True, max_length=255)
    permissions = StringListField()
    division = DivisionSerializer()

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Supplier
        fields = ['id', 'name']
        read_only_fields = ['id']

def serialize_user_profile(user):
    profile = models.Profile.objects.get(user=user)
    serializer = UserProfileSerializer({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "job_position": profile.job_position,
        "division": profile.division,
    })

    return serializer


def serialize_full_user_profile(user):
    profile = models.Profile.objects.get(user=user)
    serializer = FullUserProfileSerializer({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "job_position": profile.job_position,
        "division": profile.division,
        "permissions": user.get_group_permissions(),
    })

    return serializer


