"""
Views fro the evidence type APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from django.db.models import Q
from django.utils.translation import gettext as _

from rest_framework import views, viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from core import models

from evidence_type.serializers import (
    EvidenceTypeSerializer,
    UpdateCustomFieldSerializer
)

from custom_field.serializers import (
    CustomFieldSerializer,
)

class EvidenceTypePermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""

        if hasattr(view, 'action'):

            if view.action == 'list' or view.action == 'retrieve':
                return request.user.has_perm('core.view_evidencetype') 

            if view.action == 'create':
                return request.user.has_perm('core.add_evidencetype')

            if view.action == 'update' or view.action == 'partial_update':
                return request.user.has_perm('core.change_evidencetype') 

            if view.action == 'destroy':
                return request.user.has_perm('core.delete_evidencetype') 

        else:

            if request.method == 'GET':
                return request.user.has_perm('core.view_evidencetype') 

            if request.method == 'POST':
                return request.user.has_perm('core.add_evidencetype')

            if request.method == 'PUT' or request.method == 'PATCH':
                return request.user.has_perm('core.change_evidencetype') 

            if request.method == 'DELETE':
                return request.user.has_perm('core.delete_evidencetype') 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

@extend_schema(tags=['Evidence catalogs'])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | ViewEvidenceType] List evidence types'),
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
            ),
            OpenApiParameter(
                'group',
                OpenApiTypes.INT,
                required=False,
                description=_('Group id filter value')
            )
        ]
    ),
    create=extend_schema(
        description=_('[Protected | AddEvidenceType] Add an evidence type')
    ),
    retrieve=extend_schema(
        description=_('[Protected | ViewEvidenceType] Retrieve an evidence type by id')
    ),
    partial_update=extend_schema(
        description=_('[Protected | ChangeEvidenceType] Partial update an evidence type by id')
    ),
    update=extend_schema(
        description=_('[Protected | ChangeEvidenceType] Replace an evidence type by id')
    ),
    destroy=extend_schema(
        description=_('[Protected | DeleteEvidenceType] Delete an evidence type by id')
    ),
)
class EvidenceTypeViewSet(viewsets.ModelViewSet):
    """Viewset for manage evidence type APIs."""
    serializer_class = EvidenceTypeSerializer
    queryset = models.EvidenceType.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EvidenceTypePermission]

    def get_queryset(self):
        """Retrieve evidence types sorted by name"""
        
        # Filter objects by active status
        active_only = self.request.query_params.get('active_only')
        queryset = self.queryset
        if self.request.method == 'GET' and (active_only == None or active_only.strip().lower() == 'true'):
            queryset = queryset.filter(is_active=True)

        name = self.request.query_params.get('name')
        if name != None:
            queryset = queryset.filter(name__icontains=name)

        parent = self.request.query_params.get('parent')
        if parent != None:
            queryset = queryset.filter(parent=parent)

        group = self.request.query_params.get('group')
        if group != None:
            queryset = queryset.filter(group=group)

        return queryset.order_by('name')
        
    
    def _update_level(self, serializer):
        # Save level depending on the parent
        level = 0
        parent = serializer.validated_data.get('parent', None)
        if parent != None:
            level = parent.level + 1

        return serializer.save(level=level)

    def perform_create(self, serializer):
        """Create a new evidence type"""
        return self._update_level(serializer)

    def perform_update(self, serializer):
        """Update a evidence type"""
        return self._update_level(serializer)
    
    def perform_destroy(self, instance):
        """Destroy a evidence type"""
        children = models.EvidenceType.objects.filter(parent=instance).count()
        if(children > 0):
            raise serializers.ValidationError(_('Unable to delete parent records. Disable it instead.'))
        
        instance.delete()


@extend_schema(tags=['Evidence catalogs'])
class ListCreateCustomFieldView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, EvidenceTypePermission]

    @extend_schema(
        description=_("[Protected | ViewEvidenceType] List custom fields by evidence type id"),
        responses={200: CustomFieldSerializer(many=True)},
    )
    def get(self, request, pk):
        model = models.EvidenceType.objects.get(id=pk)
        serializer = CustomFieldSerializer(model.custom_fields.all(), many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description=_("[Protected | ChangeEvidenceType] Update evidence type custom fields by id"),
        request=UpdateCustomFieldSerializer,
        responses={200: CustomFieldSerializer(many=True)},
    )
    def put(self, request, pk):
        """Update evidence type custom fields"""
        
        # Get allowed custom fields only
        body_serializer = UpdateCustomFieldSerializer(request.data)
        cond = Q()
        for cf in body_serializer.data['custom_fields']:
            cond |= Q(id=cf)

        custom_fields = models.CustomField.objects.filter(cond)

        model = models.EvidenceType.objects.get(id=pk)
        model.custom_fields.set(custom_fields)

        serializer = CustomFieldSerializer(model.custom_fields.all(), many=True)
        return Response(serializer.data)
    