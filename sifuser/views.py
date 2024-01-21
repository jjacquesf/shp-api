"""
Views fro theSIF userAPIs
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

from sifuser.serializers import (
    SifUserSerializer
)

class SifUserPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_sifuser') 

        if view.action == 'create':
            return request.user.has_perm('core.add_sifuser')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_sifuser') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_sifuser') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewSifUser] List SIF users'),
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
        description=_('[Protected | AddSifUser] Add an SIF user')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewSifUser] Retrieve a SIF userby id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeSifUser] Partial update a SIF userby id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeSifUser] Replace a SIF userby id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteSifUser] Delete a SIF userby id')
    ),
)
class SifUserViewSet(viewsets.ModelViewSet):
    """Viewset for manageSIF userAPIs."""
    serializer_class = SifUserSerializer
    queryset = models.SifUser.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, SifUserPermission]

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