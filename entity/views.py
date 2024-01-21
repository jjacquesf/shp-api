"""
Views fro the entity APIs
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

from entity.serializers import (
    EntitySerializer
)

class EntityPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_entity') 

        if view.action == 'create':
            return request.user.has_perm('core.add_entity')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_entity') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_entity') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewEntity] List entities'),
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
                'parent',
                OpenApiTypes.INT,
                required=False,
                description=_('Parent id filter value')
            )
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddEntity] Add an entity')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewEntity] Retrieve an entity by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeEntity] Partial update an entity by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeEntity] Replace an entity by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteEntity] Delete an entity by id')
    ),
)
class EntityViewSet(viewsets.ModelViewSet):
    """Viewset for manage entity APIs."""
    serializer_class = EntitySerializer
    queryset = models.Entity.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EntityPermission]

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

        parent = self.request.query_params.get('parent')
        if parent != None:
            queryset = queryset.filter(parent=parent)

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
        children = models.Entity.objects.filter(parent=instance).count()
        if(children > 0):
            raise serializers.ValidationError(_('Unable to delete parent records. Disable it instead.'))
        
        instance.delete()