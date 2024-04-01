"""
Views fro the quality control APIs
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

from evidence_finding.serializers import (
    EvidenceFindingSerializer
)

class EvidenceFindingPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_evidencefinding') 

        if view.action == 'create':
            return request.user.has_perm('core.add_evidencefinding')
        
        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_evidencefinding') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=['Evidence catalogs'])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewEvidenceFinding] List quality control'),
        parameters=[
            OpenApiParameter(
                'evidence',
                OpenApiTypes.INT,
                required=False,
                description=_('Evidence id filter value')
            ),
            OpenApiParameter(
                'user',
                OpenApiTypes.INT,
                required=False,
                description=_('User id filter value')
            ),
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddEvidenceFinding] Add an quality control')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewEvidenceFinding] Retrieve an quality control by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeEvidenceFinding] Partial update an quality control by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeEvidenceFinding] Replace an quality control by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteEvidenceFinding] Delete an quality control by id')
    ),
)
class EvidenceFindingViewSet(viewsets.ModelViewSet):
    """Viewset for manage quality control APIs."""
    serializer_class = EvidenceFindingSerializer
    queryset = models.EvidenceFinding.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EvidenceFindingPermission]

    def get_queryset(self):
        """Retrieve quality control sorted by name"""
        active_only = self.request.query_params.get('active_only')

        # Filter objects by active status
        queryset = self.queryset

        evidence = self.request.query_params.get('evidence')
        if evidence != None:
            queryset = queryset.filter(evidence=evidence)

        qc = self.request.query_params.get('qc')
        if qc != None:
            queryset = queryset.filter(qc=qc)

        status = self.request.query_params.get('status')
        if status != None:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-id')
    
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return CreateEvidenceFindingSerializer
        
    #     return self.serializer_class

    # def perform_create(self, serializer):
    #     """Create a new quality control"""
    #     return serializer.save()
    