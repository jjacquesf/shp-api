"""
Views fro the evidence status APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core import models

from evidence_status.serializers import (
    EvidenceStatusSerializer,
    SaveEvidenceStatusSerializer
)

class EvidenceStatusPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_evidencestatus') 

        if view.action == 'create':
            return request.user.has_perm('core.add_evidencestatus')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_evidencestatus') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_evidencestatus') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=['Evidence catalogs'])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewEvidenceStatus] List evidence status'),
        parameters=[
            OpenApiParameter(
                'active_only',
                OpenApiTypes.STR,
                required=False,
                description=_('Either "true" or "false" depending on the desired query. Default: "true"')
            ),
            OpenApiParameter(
                'name',
                OpenApiTypes.STR,
                required=False,
                description=_('Name filter value')
            ),
            OpenApiParameter(
                'description',
                OpenApiTypes.STR,
                required=False,
                description=_('Description filter value')
            ),
            OpenApiParameter(
                'color',
                OpenApiTypes.STR,
                required=False,
                description=_('Color filter value')
            ),
            OpenApiParameter(
                'type',
                OpenApiTypes.INT,
                required=False,
                description=_('Type id filter value')
            ),
            OpenApiParameter(
                'stage',
                OpenApiTypes.INT,
                required=False,
                description=_('Stage id filter value')
            ),
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddEvidenceStatus] Add an evidence status')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewEvidenceStatus] Retrieve an evidence status by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeEvidenceStatus] Partial update an evidence status by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeEvidenceStatus] Replace an evidence status by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteEvidenceStatus] Delete an evidence status by id')
    ),
)
class EvidenceStatusViewSet(viewsets.ModelViewSet):
    """Viewset for manage evidence status APIs."""
    serializer_class = EvidenceStatusSerializer
    queryset = models.EvidenceStatus.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EvidenceStatusPermission]
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return SaveEvidenceStatusSerializer
        
        return self.serializer_class

    def get_queryset(self):
        """Retrieve evidence status sorted by name"""
        active_only = self.request.query_params.get('active_only')

        # Filter objects by active status
        queryset = self.queryset
        if self.request.method == 'GET' and (active_only == None or active_only.strip().lower() == 'true'):
            queryset = queryset.filter(is_active=True)

        name = self.request.query_params.get('name')
        if name != None:
            queryset = queryset.filter(name__icontains=name)

        description = self.request.query_params.get('description')
        if description != None:
            queryset = queryset.filter(description__icontains=description)

        color = self.request.query_params.get('color')
        if color != None:
            queryset = queryset.filter(color__icontains=color)

        stage = self.request.query_params.get('stage')
        if stage != None:
            queryset = queryset.filter(stage=stage)

        group = self.request.query_params.get('group')
        if group != None:
            queryset = queryset.filter(group=group)

        type = self.request.query_params.get('type')
        if type != None:
            queryset = queryset.filter(type=type)

        return queryset.order_by('name')
    

    # def perform_create(self, serializer):
    #     """Create a new evidencde status"""
    #     return self._update_level(serializer)

    # def perform_update(self, serializer):
    #     """Update a evidencde status"""
    #     return self._update_level(serializer)
    
    # def perform_destroy(self, instance):
    #     """Destroy a evidencde status"""
    #     children = models.EvidenceStatus.objects.filter(parent=instance)
    #     if(len(children)):
    #         raise serializers.ValidationError(_('Unable to delete parent records. Disable it instead.'))
        
    #     instance.delete()