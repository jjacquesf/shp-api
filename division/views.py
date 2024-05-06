"""
Views fro the division APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.contrib.auth import get_user_model

from core import models

from division.serializers import (
    DivisionSerializer
)

class DivisionPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_division') 

        if view.action == 'create':
            return request.user.has_perm('core.add_division')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_division') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_division') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | Viewdivision] List decentralized public entities'),
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
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddDivision] Add a decentralized public entity')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewDivision] Retrieve a decentralized public entity by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeDivision] Partial update a decentralized public entity by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeDivision] Replace a decentralized public entity by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteDivision] Delete a decentralized public entity by id')
    ),
)
class DivisionViewSet(viewsets.ModelViewSet):
    """Viewset for manage division APIs."""
    serializer_class = DivisionSerializer
    queryset = models.Division.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DivisionPermission]

    def get_queryset(self):
        """Retrieve decentralized public entities sorted by name"""
        active_only = self.request.query_params.get('active_only')

        # Filter objects by active status
        queryset = self.queryset
        if self.request.method == 'GET' and (active_only == None or active_only.strip().lower() == 'true'):
            queryset = queryset.filter(is_active=True)

        name = self.request.query_params.get('name')
        if name != None:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by('name')
    
    def perform_destroy(self, instance):
        """Destroy a division type"""
        profiles = models.Profile.objects.filter(division=instance)
        if len(profiles):
            users_id = map(lambda x: x.user_id, profiles)
            children = get_user_model().objects.filter(id__in=users_id).count()
            if(children > 0):
                raise serializers.ValidationError(_('No se puede eliminar porque hay registros que dependen de el. Puedes deshabilitarlo.'))

        instance.delete()