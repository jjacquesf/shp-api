"""
Views fro the SIAN userAPIs
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

from sianuser.serializers import (
    SianUserSerializer
)

class SianUserPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_sianuser') 

        if view.action == 'create':
            return request.user.has_perm('core.add_sianuser')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_sianuser') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_sianuser') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewSianUser] List SIAN users'),
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
                'stateorg',
                OpenApiTypes.INT,
                required=False,
                description=_('State Organization id filter value')
            )
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddSianUser] Add an SIAN user')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewSianUser] Retrieve a SIAN userby id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeSianUser] Partial update a SIAN userby id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeSianUser] Replace a SIAN userby id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteSianUser] Delete a SIAN userby id')
    ),
)
class SianUserViewSet(viewsets.ModelViewSet):
    """Viewset for manageSIAN userAPIs."""
    serializer_class = SianUserSerializer
    queryset = models.SianUser.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, SianUserPermission]

    def get_queryset(self):
        """Retrieve entities sorted by name"""
        active_only = self.request.query_params.get('active_only')

        # Filter objects by active status
        queryset = self.queryset
        if self.request.method == 'GET' and (active_only == None or active_only.strip().lower() == 'true'):
            queryset = queryset.filter(is_active=True)

        name = self.request.query_params.get('name')
        if name != None:
            queryset = queryset.filter(name__icontains=name)

        stateorg = self.request.query_params.get('stateorg')
        if stateorg != None:
            queryset = queryset.filter(stateorg=stateorg)

        return queryset.order_by('name')