"""
Serializer for the user API view
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _
from group.serializers import StringListField

from rest_framework import serializers
from core import models

from core.serializers import (
    IntegerListField,
)


class EvidenceSerializer(serializers.Serializer):
    """Serializer for user creation."""
    id = serializers.IntegerField(required=False)
    type = serializers.IntegerField(required=True)
    owner = serializers.IntegerField(required=True)
    status = serializers.IntegerField(required=True)
    dirty = serializers.BooleanField(default=False)
    pending_auth = serializers.BooleanField(default=False)
    pending_signature = serializers.BooleanField(default=False)
    version = serializers.IntegerField(required=True)

def serialize_evidence(model):
    evidence = models.Evidence.objects.get(id=model.id)
    serializer = EvidenceSerializer({
        "id": evidence.id,
        "type": evidence.type.id,
        "owner": evidence.owner.id,
        "status": evidence.status.id,
        "dirty": evidence.dirty,
        "pending_auth": evidence.pending_auth,
        "pending_signature": evidence.pending_signature,
        "version": evidence.version,
        # "permissions": user.get_group_permissions(),
    })

    return serializer


class CreateEvidenceSerializer(serializers.Serializer):
    """Serializer for user creation."""
    id = serializers.IntegerField(required=False)
    type = serializers.IntegerField(required=True)
    signers = IntegerListField()
    authorizers = IntegerListField()
    # owner = serializers.IntegerField(required=True)
    # status = serializers.IntegerField(required=True)
    # dirty = serializers.BooleanField(default=False)
    # pending_auth = serializers.BooleanField(default=False)
    # pending_signature = serializers.BooleanField(default=False)
    # version = serializers.IntegerField(required=True)
