"""
Views fro the theme APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core import models

from theme.serializers import (
    ThemeSerializer
)

class ThemePermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'create' or  view.action == 'partial_update' or view.action == 'destroy':
            return False

        if view.action == 'retrieve':
            return request.user.has_perm('core.view_theme') 


        if view.action == 'update':
            return request.user.has_perm('core.change_theme') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    retrieve=extend_schema(
        description=_('[Protected | ViewTheme] Retrieve a theme by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeTheme] Replace a theme by id')
    ),
)
class ThemeViewSet(viewsets.ModelViewSet):
    """Viewset for manage theme APIs."""
    serializer_class = ThemeSerializer
    queryset = models.Theme.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ThemePermission]

    def get_queryset(self):
        """Retrieve theme sorted by name"""
        queryset = self.queryset

        return queryset

    # def perform_create(self, serializer):
    #     """Create a new theme"""
    #     # Validate something