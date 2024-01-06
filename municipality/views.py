"""
Views fro the municipality APIs
"""
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

        return True
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

class MunicipalityViewSet(viewsets.ModelViewSet):
    """Viewset for manage municipality APIs."""
    serializer_class = MunicipalitySerializer
    queryset = models.Municipality.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, MunicipalityPermission]

    def get_queryset(self):
        """Retrieve municipalities sorted by name"""
        return self.queryset.order_by('name')

    # def perform_create(self, serializer):
    #     """Create a new municipality"""
    #     # Validate something