"""
Views fro the supplier APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core import models

from supplier.serializers import (
    SupplierSerializer
)

class SupplierPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if view.action == 'list' or view.action == 'retrieve':
            return request.user.has_perm('core.view_supplier') 

        if view.action == 'create':
            return request.user.has_perm('core.add_supplier')

        if view.action == 'update' or view.action == 'partial_update':
            return request.user.has_perm('core.change_supplier') 

        if view.action == 'destroy':
            return request.user.has_perm('core.delete_supplier') 

        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=[_('Catalogs')])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewSupplier] List suppliers'),
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
                'tax_id',
                OpenApiTypes.STR,
                required=False,
                description=_('Tax ID filter value')
            ),
            OpenApiParameter(
                'tax_name',
                OpenApiTypes.STR,
                required=False,
                description=_('Tax name filter value')
            ),
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddSupplier] Add a supplier')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewSupplier] Retrieve a supplier by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeSupplier] Partial update a supplier by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeSupplier] Replace a supplier by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteSupplier] Delete a supplier by id')
    ),
)
class SupplierViewSet(viewsets.ModelViewSet):
    """Viewset for manage supplier APIs."""
    serializer_class = SupplierSerializer
    queryset = models.Supplier.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, SupplierPermission]

    def get_queryset(self):
        """Retrieve suppliers sorted by name"""
        active_only = self.request.query_params.get('active_only')

        # Filter objects by active status
        queryset = self.queryset
        if self.request.method == 'GET' and (active_only == None or active_only.strip().lower() == 'true'):
            queryset = queryset.filter(is_active=True)

        name = self.request.query_params.get('name')
        if name != None:
            queryset = queryset.filter(name__icontains=name)

        tax_id = self.request.query_params.get('tax_id')
        if tax_id != None:
            queryset = queryset.filter(tax_id__icontains=tax_id)

        tax_name = self.request.query_params.get('tax_name')
        if tax_name != None:
            queryset = queryset.filter(tax_name__icontains=tax_name)
            
        return queryset.order_by('name')

    # def perform_create(self, serializer):
    #     """Create a new supplier"""
    #     # Validate something