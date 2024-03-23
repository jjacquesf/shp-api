"""
Serializer for the user API view
"""
import json
from django.forms.models import model_to_dict

from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _
from group.serializers import StringListField

from rest_framework import serializers
from django.contrib.auth import get_user_model

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
    eav = serializers.CharField(required=False)

def serialize_evidence(model):
    evidence = models.Evidence.objects.get(id=model.id)

    attrs = evidence.eav_values.all()
    eav = []
    for attr in attrs:
        eav.append(model_to_dict(attr))

    # print()

    serializer = EvidenceSerializer({
        "id": evidence.id,
        "type": evidence.type.id,
        # "parent": evidence.parent.id,
        "owner": evidence.owner.id,
        # "uploaded_file": evidence.uploaded_file.id,
        "status": evidence.status.id,
        "dirty": evidence.dirty,
        "pending_auth": evidence.pending_auth,
        "pending_signature": evidence.pending_signature,
        "version": evidence.version,
        # "permissions": user.get_group_permissions(),
        "eav": json.dumps(eav, default=str)
    })

    return serializer

class CreateEvidenceSerializer(serializers.Serializer):
    """Serializer for user creation."""
    # id = serializers.IntegerField(required=False)
    owner_id = serializers.IntegerField(required=False)
    status_id = serializers.IntegerField(required=True)
    type_id = serializers.IntegerField(required=True)
    parent_id = serializers.IntegerField(required=False)
    uploaded_file_id = serializers.IntegerField(required=False)
    authorizers = IntegerListField(required=False)
    signers = IntegerListField(required=False)
    eav = serializers.CharField(required=False)

    def create(self, validated_data):

        owner = get_user_model().objects.get(id=validated_data.get('owner_id'))

        type = models.EvidenceType.objects.get(id=validated_data.get('type_id'))

        status = models.EvidenceStatus.objects.get(id=validated_data.get('status_id'), group=type.group)

        parent = validated_data.get('parent_id')
        if parent != None:
            parent = models.Evidence.objects.get(id=parent)

        uploaded_file = validated_data.get('uploaded_file_id')
        if uploaded_file != None:
            uploaded_file = models.UploadedFile.objects.get(id=uploaded_file)
            
        pending_auth = False
        authorizers = validated_data.get('authorizers')
        if authorizers != None and len(authorizers) > 0:
            pending_auth = True

        pending_signature = False
        signers = validated_data.get('signers')
        if signers != None and len(signers) > 0:
            pending_signature = True

        data = {
            "status": status,
            "type": type,
            "parent": parent,
            "uploaded_file": uploaded_file,
            "type": type,
            "owner": owner,
            "pending_auth": pending_auth,
            "pending_signature": pending_signature,
            "dirty": False,
            "version": 1
        }

        eav = validated_data.get('eav')
        eav_attrs = json.loads(eav)

        data = {
            **data,
            **eav_attrs
        }

        evidence = models.Evidence.objects.create(**data)

        for v in authorizers:
            user = get_user_model().objects.get(id=v)
            data = {
                "status": "PEN",
                "evidence": evidence,
                "user": user,
                "version": 1
            }
            models.EvidenceAuth.objects.create(**data)

        for v in signers:
            user = get_user_model().objects.get(id=v)
            data = {
                "status": "PEN",
                "evidence": evidence,
                "user": user,
                "version": 1
            }
            models.EvidenceSignature.objects.create(**data)

        serializer = serialize_evidence(evidence)

        return serializer.data

