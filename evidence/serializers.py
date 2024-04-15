"""
Serializer for the user API view
"""
from datetime import datetime
import json
from django.core.exceptions import ObjectDoesNotExist


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

from evidence_group.serializers import (
    EvidenceGroupSerializer
)

from evidence_type.serializers import (
    EvidenceTypeSerializer,
)

from evidence_status.serializers import (
    EvidenceStatusSerializer
)

from user.serializers import (
    BaseUserSerializer
)

from assets.serializers import (
    FileUploadSerializer,
)



class EvidenceAuthSerializer(serializers.ModelSerializer):
    """Serializer for evidence auth creation."""
    user = BaseUserSerializer()
    class Meta:
        model=models.EvidenceAuth
        fields = ['evidence', 'status', 'user', 'version']

class EvidenceSignatureSerializer(serializers.ModelSerializer):
    """Serializer for evidence auth creation."""
    user = BaseUserSerializer()
    class Meta:
        model=models.EvidenceSignature
        fields = ['evidence', 'status', 'user', 'version']


class EvidenceSerializer(serializers.ModelSerializer):
    """Serializer for evidence creation."""

    authorizers = serializers.SerializerMethodField()
    signers = serializers.SerializerMethodField()
    eav = serializers.SerializerMethodField()

    status = EvidenceStatusSerializer()
    group = EvidenceGroupSerializer()
    owner = BaseUserSerializer()
    creator = BaseUserSerializer()
    type = EvidenceTypeSerializer()
    uploaded_file = FileUploadSerializer()

    class Meta:
        model=models.Evidence
        fields = ['id', 'owner', 'creator', 'status', 'status', 'group', 'type', 'parent', 'uploaded_file', 'authorizers', 'signers', 'eav']

    def get_authorizers(self, obj):
        rows = models.EvidenceAuth.objects.filter(evidence=obj)
        s = EvidenceAuthSerializer(rows, many=True)
        return s.data

    def get_signers(self, obj):
        rows = models.EvidenceSignature.objects.filter(evidence=obj)
        s = EvidenceSignatureSerializer(rows, many=True)
        return s.data
    
    def get_eav(self, obj):
        eav = {}
        custom_fields = models.EvidenceTypeCustomField.objects.filter(type=obj.type)
        for cf in custom_fields:
            value = getattr(obj.eav, cf.custom_field.attribute.slug)
            eav.update({cf.custom_field.attribute.slug: value})
        return eav

class CreateEvidenceSerializer(serializers.Serializer):
    """Serializer for user creation."""
    owner = serializers.IntegerField(required=False)
    creator = serializers.IntegerField(required=False)
    # status = serializers.IntegerField(required=True)
    type = serializers.IntegerField(required=True)
    group = serializers.IntegerField(required=False)
    parent = serializers.IntegerField(required=False)
    uploaded_file = serializers.IntegerField(required=False)
    authorizers = IntegerListField(required=False)
    signers = IntegerListField(required=False)
    eav = serializers.CharField(required=False)

    def create(self, validated_data):

        owner = get_user_model().objects.get(id=validated_data.get('owner'))
        creator = get_user_model().objects.get(id=validated_data.get('creator'))

        group = models.EvidenceGroup.objects.get(id=validated_data.get('group'))
        type = models.EvidenceType.objects.get(id=validated_data.get('type'))
        
        parent = validated_data.get('parent')
        if parent != None:
            parent = models.Evidence.objects.get(id=parent)

        uploaded_file = validated_data.get('uploaded_file')
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
            "group": group,
            "type": type,
            "status": type.creation_status,
            "parent": parent,
            "uploaded_file": uploaded_file,
            "creator": creator,
            "owner": owner,
            "pending_auth": pending_auth,
            "pending_signature": pending_signature,
            "dirty": False,
            "version": 1
        }

        evidence = models.Evidence.objects.create(**data)


        custom_fields = models.EvidenceTypeCustomField.objects.filter(type=type)
        eav = validated_data.get('eav')
        if eav != None:
            eav_attrs = json.loads(eav)
            for k in eav_attrs:
                attrs = [x for x in custom_fields if x.custom_field.attribute.slug == k]
                if len(attrs) and attrs[0].custom_field.attribute.datatype == "date":
                    try:
                        date = datetime.strptime(eav_attrs[k], '%Y-%m-%d').date()
                        setattr(evidence.eav, k, date)
                    except ValueError as ve1:
                        setattr(evidence.eav, k, None)
                else:
                    setattr(evidence.eav, k, eav_attrs[k])

        evidence.save()

        # Create authorizers
        if authorizers != None:
            for v in authorizers:
                user = get_user_model().objects.get(id=v)
                try:
                    models.EvidenceAuth.objects.get(evidence=evidence, user=user)
                except ObjectDoesNotExist:
                    data = {
                        "status": "PEN",
                        "evidence": evidence,
                        "user": user,
                        "version": 1
                    }
                    models.EvidenceAuth.objects.create(**data)

        # Create signers
        if signers != None:
            for v in signers:
                user = get_user_model().objects.get(id=v)
                try:
                    models.EvidenceSignature.objects.get(evidence=evidence, user=user)
                except ObjectDoesNotExist:
                    data = {
                        "status": "PEN",
                        "evidence": evidence,
                        "user": user,
                        "version": 1
                    }
                    models.EvidenceSignature.objects.create(**data)

        serializer = EvidenceSerializer(evidence)
        return serializer.data
    
class UpdateEvidenceSerializer(serializers.ModelSerializer):
    eav = serializers.CharField(required=False)
    
    class Meta:
        model=models.Evidence
        fields = ['status',
                  'uploaded_file',
                  'eav'
                  ]