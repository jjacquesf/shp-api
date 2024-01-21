"""
Views fro the municipality APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core import models

from municipality.serializers import (
    MunicipalitySerializer
)

class MunicipalityPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_municipality') 

        if view.action == 'create':
            return request.user.has_perm('core.add_municipality')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_municipality') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_municipality') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewMunicipality] List municipalities'),
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
        description=_('[Protected | AddMunicipality] Add a municipality')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewMunicipality] Retrieve a municipality by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeMunicipality] Partial update a municipality by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeMunicipality] Replace a municipality by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteMunicipality] Delete a municipality by id')
    ),
)
class MunicipalityViewSet(viewsets.ModelViewSet):
    """Viewset for manage municipality APIs."""
    serializer_class = MunicipalitySerializer
    queryset = models.Municipality.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, MunicipalityPermission]

    def get_queryset(self):
        """Retrieve municipalities sorted by name"""
        active_only = self.request.query_params.get('active_only')

        # Filter objects by active status
        queryset = self.queryset
        if self.request.method == 'GET' and (active_only == None or active_only.strip().lower() == 'true'):
            queryset = queryset.filter(is_active=True)

        name = self.request.query_params.get('name')
        if name != None:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by('name')

    # def perform_create(self, serializer):
    #     """Create a new municipality"""
    #     # Validate something