"""
Views fro the evidence APIs
"""
from datetime import datetime
import json
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core import models

from evidence.serializers import (
    CreateEvidenceSerializer,
    EvidenceSerializer,
    UpdateEvidenceSerializer
)

class EvidencePermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_evidence') or request.user.has_perm('core.manage_evidence')  or request.user.has_perm('core.work_evidence') 

        if view.action == 'create':
            return request.user.has_perm('core.add_evidence') or request.user.has_perm('core.manage_evidence')  or request.user.has_perm('core.work_evidence') 

        # if view.action == 'update' or view.action == 'partial_update':
        if view.action == 'partial_update':
            return request.user.has_perm('core.change_evidence') or request.user.has_perm('core.manage_evidence')  or request.user.has_perm('core.work_evidence') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_evidence') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""

        print('========')
        print('========')
        print('========')
        print('========')
        print('========')
        print(view)
        print('========')
        print('========')
        print('========')
        print('========')
        print(obj)
        print('========')
        print('========')
        print('========')
        print('========')
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewEvidence] List evidences'),
        parameters=[
            OpenApiParameter(
                'owner',
                OpenApiTypes.INT,
                required=False,
                description=_('Owner filter value')
            ),
            OpenApiParameter(
                'parent',
                OpenApiTypes.INT,
                required=False,
                description=_('Parent id filter value')
            )
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddEvidence] Add an evidence')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewEvidence] Retrieve an evidence by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeEvidence] Partial update an evidence by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeEvidence] Replace an evidence by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteEvidence] Delete an evidence by id')
    ),
)
class EvidenceViewSet(viewsets.ModelViewSet):
    """Viewset for manage evidence APIs."""
    serializer_class = EvidenceSerializer
    queryset = models.Evidence.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EvidencePermission]


    def get_serializer_class(self):
        if self.action == 'create':
            return CreateEvidenceSerializer
        
        if self.action == 'partial_update':
            return UpdateEvidenceSerializer

        return self.serializer_class

    def get_queryset(self):
        """Retrieve evidences sorted by name"""
        # Filter objects by active status
        queryset = self.queryset

        owner = self.request.query_params.get('owner')
        if owner != None:
            queryset = queryset.filter(owner=owner)

        status = self.request.query_params.get('status')
        if status != None:
            queryset = queryset.filter(status=status)

        group = self.request.query_params.get('group')
        if group != None:
            queryset = queryset.filter(group=group)

        type = self.request.query_params.get('type')
        if type != None:
            queryset = queryset.filter(type=type)

        parent = self.request.query_params.get('parent')
        if parent != None:
            queryset = queryset.filter(parent=parent)

        return queryset.order_by('-id')
    
    def perform_create(self, serializer):
        """Create a new evidence"""
        
        type = models.EvidenceType.objects.get(id=serializer.validated_data.get('type'))
        owner = serializer.validated_data.get('owner')
        if type.is_owner_open == False or owner == None:
            payload={'group': type.group.id, 'owner': self.request.user.id,  'creator': self.request.user.id}
            payload.update(serializer.validated_data)
        else:
            payload={'group': type.group.id, 'creator': self.request.user.id}
            payload.update(serializer.validated_data)

        s = CreateEvidenceSerializer(data=payload)
        s.is_valid(raise_exception=True)
        return s.save()
    
    def perform_update(self, serializer):
        """Update a evidence"""
        
        instance = self.get_object() 

        custom_fields = models.EvidenceTypeCustomField.objects.filter(type=instance.type)
        eav = serializer.validated_data.get('eav')
        if eav != None:
            eav_attrs = json.loads(eav)
            print(eav_attrs)
            for k in eav_attrs:
                attrs = [x for x in custom_fields if x.custom_field.attribute.slug == k]
                if len(attrs) and attrs[0].custom_field.attribute.datatype == "date":
                    try:
                        date = datetime.strptime(eav_attrs[k], '%Y-%m-%d').date()
                        setattr(instance.eav, k, date)
                    except ValueError as ve1:
                        setattr(instance.eav, k, None)
                else:
                    setattr(instance.eav, k, eav_attrs[k])

        status = serializer.validated_data.get('status')
        if status != None:
            instance.status = status

        uploaded_file = serializer.validated_data.get('uploaded_file')
        if uploaded_file != None:
            instance.uploaded_file = uploaded_file

        instance.version = instance.version + 1
        instance.save()

        instance.refresh_from_db()

        s = EvidenceSerializer(instance)
        return s.data