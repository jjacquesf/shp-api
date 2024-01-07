"""
Views fro the state organization APIs
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

from state_org.serializers import (
    StateOrgSerializer
)

class StateOrgPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_stateorg') 

        if view.action == 'create':
            return request.user.has_perm('core.add_stateorg')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_stateorg') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_stateorg') 

        return True
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewStateOrg] List entities'),
        parameters=[
            OpenApiParameter(
                'active_only',
                OpenApiTypes.STR,
                required=False,
                description=_('Either "true" or "false" depending on the desired query. Default: "true"')
            )
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddStateOrg] Add an state organization')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewStateOrg] Retrieve an state organization by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeStateOrg] Partial update an state organization by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeStateOrg] Replace an state organization by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteStateOrg] Delete an state organization by id')
    ),
)
class StateOrgViewSet(viewsets.ModelViewSet):
    """Viewset for manage state organization APIs."""
    serializer_class = StateOrgSerializer
    queryset = models.StateOrg.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, StateOrgPermission]

    def get_queryset(self):
        """Retrieve entities sorted by name"""
        active_only = self.request.query_params.get('active_only')

        # Filter objects by active status
        queryset = self.queryset
        if active_only == None or active_only.strip().lower() == 'true':
            queryset = queryset.filter(is_active=True)

        return queryset.order_by('name')
    
    def _update_level(self, serializer):
        # Save level depending on the parent
        level = 0
        parent = serializer.validated_data.get('parent', None)
        if parent != None:
            level = parent.level + 1

        return serializer.save(level=level)

    def perform_create(self, serializer):
        """Create a new supplier"""
        return self._update_level(serializer)

    def perform_update(self, serializer):
        """Update a supplier"""
        return self._update_level(serializer)
    
    def perform_destroy(self, instance):
        """Destroy a supplier"""
        children = models.StateOrg.objects.filter(parent=instance)
        if(len(children)):
            raise serializers.ValidationError(_('Unable to delete parent records. Disable it instead.'))
        
        instance.delete()