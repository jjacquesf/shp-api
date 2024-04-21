"""
Views fro the evidence status APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core import models

from evidence_quality_control.serializers import (
    CreateEvidenceQualityControlSerializer,
    EvidenceQualityControlSerializer,
    UpdateEvidenceQualityControlSerializer
)

class EvidenceQualityControlPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'create':
            return request.user.has_perm('core.add_qualitycontrol') 

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_qualitycontrol') 
        
        if view.action == 'partial_update':
            return request.user.has_perm('core.change_qualitycontrol') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True


@extend_schema(tags=['Evidence catalogs'])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewEvidenceQualityControl] List evidence status'),
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
        description=_('[Protected | AddEvidence] Add an evidence quality control')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewEvidence] Retrieve an evidence quality control by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeEvidence] Partial update an evidence quality control by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeEvidence] Replace an evidence quality control by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteEvidence] Delete an evidence quality control by id')
    ),
)
class EvidenceQualityControlViewSet(viewsets.ModelViewSet):
    """Viewset for manage evidence status APIs."""
    serializer_class = EvidenceQualityControlSerializer
    queryset = models.EvidenceQualityControl.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EvidenceQualityControlPermission]

    def get_queryset(self):
        """Retrieve evidence status sorted by name"""
        # Filter objects by active status
        queryset = self.queryset

        status = self.request.query_params.get('status')
        if status != None:
            queryset = queryset.filter(status=status)

        evidence = self.request.query_params.get('evidence')
        if evidence != None:
            queryset = queryset.filter(evidence=evidence)

        user = self.request.query_params.get('user')
        if user != None:
            queryset = queryset.filter(user=user)

        quality_control = self.request.query_params.get('quality_control')
        if quality_control != None:
            queryset = queryset.filter(quality_control=quality_control)

        return queryset.order_by('-id')
    

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateEvidenceQualityControlSerializer
        
        if self.request.method == 'PATCH':
            return UpdateEvidenceQualityControlSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new evidence quality control"""

        payload={'user': self.request.user.id}
        payload.update(serializer.data)

        s = CreateEvidenceQualityControlSerializer(data=payload)
        s.is_valid(raise_exception=True)
        return s.save()
    