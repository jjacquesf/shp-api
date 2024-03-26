"""
Serializer for the user API view
"""
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

class EvidenceAuthSerializer(serializers.ModelSerializer):
    """Serializer for evidence auth creation."""
    class Meta:
        model=models.EvidenceAuth
        fields = ['evidence', 'status', 'user', 'version']

class EvidenceSignatureSerializer(serializers.ModelSerializer):
    """Serializer for evidence auth creation."""
    class Meta:
        model=models.EvidenceSignature
        fields = ['evidence', 'status', 'user', 'version']


class EvidenceSerializer(serializers.ModelSerializer):
    """Serializer for evidence creation."""

    authorizers = serializers.SerializerMethodField()
    signers = serializers.SerializerMethodField()

    class Meta:
        model=models.Evidence
        fields = ['owner', 'status', 'status', 'type', 'parent', 'uploaded_file', 'authorizers', 'signers']
        read_only_fields = ['id']

    def get_authorizers(self, obj):
        rows = models.EvidenceAuth.objects.filter(evidence=obj)
        s = EvidenceAuthSerializer(rows, many=True)
        return s.data
    

    def get_signers(self, obj):
        rows = models.EvidenceSignature.objects.filter(evidence=obj)
        s = EvidenceSignatureSerializer(rows, many=True)
        return s.data
    
class CreateEvidenceSerializer(serializers.Serializer):
    """Serializer for user creation."""
    owner = serializers.IntegerField(required=False)
    status = serializers.IntegerField(required=True)
    type = serializers.IntegerField(required=True)
    parent = serializers.IntegerField(required=False)
    uploaded_file = serializers.IntegerField(required=False)
    authorizers = IntegerListField(required=False)
    signers = IntegerListField(required=False)
    eav = serializers.CharField(required=False)

    def create(self, validated_data):

        owner = get_user_model().objects.get(id=validated_data.get('owner'))

        type = models.EvidenceType.objects.get(id=validated_data.get('type'))
        status = models.EvidenceStatus.objects.get(id=validated_data.get('status'), group=type.group)

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
            "status": status,
            "type": type,
            "parent": parent,
            "uploaded_file": uploaded_file,
            "owner": owner,
            "pending_auth": pending_auth,
            "pending_signature": pending_signature,
            "dirty": False,
            "version": 1
        }

        evidence = models.Evidence.objects.create(**data)


        eav = validated_data.get('eav')
        if eav != None:
            eav_attrs = json.loads(eav)
            for k in eav_attrs:
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

class PartialUpdateEvidenceSerializer(serializers.Serializer):
    """Serializer for user creation."""
    owner = serializers.IntegerField(required=True)
    status = serializers.IntegerField(required=False)
    uploaded_file = serializers.IntegerField(required=False)
    authorizers = IntegerListField(required=False)
    signers = IntegerListField(required=False)
    eav = serializers.CharField(required=False)

    def update(self, instance, validated_data):


        status = validated_data.get('status')
        if status != None:
            instance.status = models.EvidenceStatus.objects.get(id=status, group=instance.type.group)

        uploaded_file = validated_data.get('uploaded_file')
        if uploaded_file != None:
            instance.uploaded_file = models.UploadedFile.objects.get(id=uploaded_file)
        
        eav = validated_data.get('eav')
        if eav != None:
            eav_attrs = json.loads(eav)
            for k in eav_attrs:
                setattr(instance.eav, k, eav_attrs[k])

        instance.version = instance.version + 1
        instance.save()


        # Delete not requiered authorizations
        current_auths = models.EvidenceAuth.objects.filter(evidence=instance)
        current_ids = [item.id for item in current_auths]
        
        authorizers = validated_data.get('authorizers')
        if authorizers != None:
            s = set(authorizers)
            delete_ids = [x for x in current_ids if x not in s]

            for di in delete_ids:
                models.EvidenceAuth.objects.filter(id=di).delete()

            ## Create athorizers
            s = set(current_ids)
            to_add_ids = [x for x in authorizers if x not in s]
            for v in to_add_ids:
                user = get_user_model().objects.get(id=v)
                try:
                    models.EvidenceAuth.objects.get(evidence=instance, user=user)
                except ObjectDoesNotExist:
                    data = {
                        "status": "PEN",
                        "evidence": instance,
                        "user": user,
                        "version": 1
                    }
                    models.EvidenceAuth.objects.create(**data)



        # Delete not requiered signatures
        current_signers = models.EvidenceSignature.objects.filter(evidence=instance)
        current_ids = [item.id for item in current_signers]
        
        signers = validated_data.get('signers')
        if signers != None:
            s = set(signers)
            delete_ids = [x for x in current_ids if x not in s]

            for di in delete_ids:
                models.EvidenceSignature.objects.filter(id=di).delete()

            ## Create athorizers
            s = set(current_ids)
            to_add_ids = [x for x in signers if x not in s]
            for v in to_add_ids:
                user = get_user_model().objects.get(id=v)
                try:
                    models.EvidenceSignature.objects.get(evidence=instance, user=user)
                except ObjectDoesNotExist:
                    data = {
                        "status": "PEN",
                        "evidence": instance,
                        "user": user,
                        "version": 1
                    }
                    models.EvidenceSignature.objects.create(**data)



        s = EvidenceSerializer(instance)
        return s.data