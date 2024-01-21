"""
Views fro the custom field APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from django.db.models import Q
from django.utils.translation import gettext as _

from eav.models import Attribute

from rest_framework import views, viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from core import models

from custom_field.serializers import (
    CustomFieldSerializer,
    CreateCustomFieldSerializer,
    UpdateCustomFieldSerializer,
)

class CustomFieldPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if hasattr(view, 'action'):

            if view.action == 'list' or view.action == 'retrieve':
                return request.user.has_perm('core.view_customfield') 

            if view.action == 'create':
                return request.user.has_perm('core.add_customfield')

            if view.action == 'partial_update':
                return request.user.has_perm('core.change_customfield') 

            if view.action == 'destroy':
                return request.user.has_perm('core.delete_customfield') 

        else:

            if request.method == 'GET':
                return request.user.has_perm('core.view_customfield') 

            if request.method == 'POST':
                return request.user.has_perm('core.add_customfield')

            if request.method == 'PATCH':
                return request.user.has_perm('core.change_customfield') 

            if request.method == 'DELETE':
                return request.user.has_perm('core.delete_customfield') 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=['Evidence catalogs'])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewCustomField] List custom fields'),
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
        description=_('[Protected | AddCustomField] Add an custom field')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewCustomField] Retrieve an custom field by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeCustomField] Partial update an custom field by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeCustomField] Replace an custom field by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteCustomField] Delete an custom field by id')
    ),
)
class CustomFieldViewSet(viewsets.ModelViewSet):
    """Viewset for manage custom field APIs."""
    serializer_class = CustomFieldSerializer
    queryset = models.CustomField.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CustomFieldPermission]

    def get_queryset(self):
        """Retrieve custom fields sorted by name"""
        
        # Filter objects by active status
        active_only = self.request.query_params.get('active_only')
        queryset = self.queryset
        if self.request.method == 'GET' and (active_only == None or active_only.strip().lower() == 'true'):
            queryset = queryset.filter(is_active=True)

        name = self.request.query_params.get('name')
        if name != None:
            queryset = queryset.filter(attribute__name__icontains=name)

        return queryset.order_by('attribute__name')
        
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCustomFieldSerializer
        
        if self.request.method == 'PATCH':
            return UpdateCustomFieldSerializer
        
        return self.serializer_class
    
    def perform_destroy(self, instance):
        """Destroy a custom field"""
        evidence_types = models.EvidenceType.objects.filter(custom_fields__id = instance.id).count()
        if(evidence_types > 0):
            raise serializers.ValidationError(_('Unable to delete record. It has evidence type dependant records. Disable it instead.'))
        
        Attribute.objects.filter(id=instance.attribute_id).delete()
        
        instance.delete()

