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

from evidence_comment.serializers import (
    CreateEvidenceCommentSerializer,
    EvidenceCommentSerializer
)

class EvidenceCommentPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_evidencecomment') 

        if view.action == 'create':
            return request.user.has_perm('core.add_evidencecomment')

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=['Evidence catalogs'])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewEvidenceComment] List evidence status'),
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
        description=_('[Protected | AddEvidenceComment] Add an evidence status')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewEvidenceComment] Retrieve an evidence status by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeEvidenceComment] Partial update an evidence status by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeEvidenceComment] Replace an evidence status by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteEvidenceComment] Delete an evidence status by id')
    ),
)
class EvidenceCommentViewSet(viewsets.ModelViewSet):
    """Viewset for manage evidence status APIs."""
    serializer_class = EvidenceCommentSerializer
    queryset = models.EvidenceComment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EvidenceCommentPermission]

    def get_queryset(self):
        """Retrieve evidence status sorted by name"""
        # Filter objects by active status
        queryset = self.queryset

        evidence = self.request.query_params.get('evidence')
        if evidence != None:
            queryset = queryset.filter(evidence=evidence)

        user = self.request.query_params.get('user')
        if user != None:
            queryset = queryset.filter(user=user)

        return queryset.order_by('-id')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateEvidenceCommentSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new evidence"""

        payload={'user': self.request.user.id}
        payload.update(serializer.data)

        s = CreateEvidenceCommentSerializer(data=payload)
        s.is_valid(raise_exception=True)
        return s.save()
    