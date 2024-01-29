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
from rest_framework import status

from core import models

from evidence_type.serializers import (
    EvidenceTypeSerializer,
    AddEvidenceTypeCustomFieldSerializer,
    UpdateEvidenceTypeCustomFieldSerializer,
    QualityControlSerializer,
    AddPatchQualityControlSerializer,
)

from custom_field.serializers import (
    CustomFieldSerializer,
    EvidenceTypeCustomFielderializer,
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

## CustomField
@extend_schema(tags=['Evidence catalogs'])
class ListCreateCustomFieldView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, EvidenceTypePermission]

    @extend_schema(
        description=_("[Protected | ViewEvidenceType] List evidence type custom fields"),
        responses={200: EvidenceTypeCustomFielderializer(many=True)},
    )
    def get(self, request, pk):
        model = models.EvidenceType.objects.get(id=pk)

        custom_fields = models.EvidenceTypeCustomField.objects.filter(type=model.id)
        serializer = EvidenceTypeCustomFielderializer(custom_fields, many=True)

        return Response(serializer.data)
    
    @extend_schema(
        description=_("[Protected | ChangeEvidenceType] Add an evidence type custom field"),
        request=AddEvidenceTypeCustomFieldSerializer,
        responses={200: EvidenceTypeCustomFielderializer},
    )
    def post(self, request, pk):
        """Update evidence type custom fields"""
        body_serializer = AddEvidenceTypeCustomFieldSerializer(data=request.data)    
        body_serializer.is_valid(raise_exception=True)

        model = models.EvidenceType.objects.get(id=pk)

        custom_field = models.CustomField.objects.get(id=body_serializer.validated_data['custom_field'])

        if custom_field != None:
            model.custom_fields.add(custom_field, through_defaults={'mandatory': body_serializer.validated_data['mandatory']})

        custom_field = models.EvidenceTypeCustomField.objects.get(type=model.id, custom_field=custom_field.id)
        serializer = EvidenceTypeCustomFielderializer(custom_field)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@extend_schema(tags=['Evidence catalogs'])
class PatchDeleteCustomFieldView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, EvidenceTypePermission]
    @extend_schema(
        description=_("[Protected | DeleteEvidenceType] Delete evidence type custom fields by id"),
        responses={200: CustomFieldSerializer(many=True)},
    )
    def delete(self, request, pk, cf_id):
        """Delete evidence type custom fields"""
        evidence_type = models.EvidenceType.objects.get(id=pk)
        models.EvidenceTypeCustomField.objects.filter(id=cf_id, type=evidence_type.id).delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        description=_("[Protected |ChangeEvidenceType]Change evidence type custom fields by id"),
        request=UpdateEvidenceTypeCustomFieldSerializer,
        responses={200: CustomFieldSerializer},
    )
    def patch(self, request, pk, cf_id):
        """Update evidence type custom field"""
        evidence_type = models.EvidenceType.objects.get(id=pk)
        custom_field = models.CustomField.objects.get(id=cf_id)

        # Update here
        body_serializer = UpdateEvidenceTypeCustomFieldSerializer(data=request.data)    
        body_serializer.is_valid(raise_exception=True)

        models.EvidenceTypeCustomField.objects.filter(type=evidence_type.id, custom_field=custom_field.id).update(**body_serializer.validated_data)

        # Return
        type_custom_field = models.EvidenceTypeCustomField.objects.get(type=evidence_type.id, custom_field=custom_field.id)

        serializer = EvidenceTypeCustomFielderializer(type_custom_field)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
## Quality control


@extend_schema(tags=['Evidence catalogs'])
class ListCreateQualityControlView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, EvidenceTypePermission]

    @extend_schema(
        description=_("[Protected | ViewEvidenceType] List evidence type quality controls"),
        responses={200: QualityControlSerializer(many=True)},
    )
    def get(self, request, pk):
        model = models.EvidenceType.objects.get(id=pk)

        custom_fields = models.QualityControl.objects.filter(type=model.id)
        serializer = QualityControlSerializer(custom_fields, many=True)

        return Response(serializer.data)
    
    @extend_schema(
        description=_("[Protected | ChangeEvidenceType] Add an evidence type quality control"),
        request=AddPatchQualityControlSerializer,
        responses={200: QualityControlSerializer},
    )
    def post(self, request, pk):
        """Add evidence type quality controls"""
        body_serializer = AddPatchQualityControlSerializer(data=request.data)    
        body_serializer.is_valid(raise_exception=True)

        type = models.EvidenceType.objects.get(id=pk)

        qc = models.QualityControl.objects.create(
            type=type,
            **body_serializer.validated_data
        )

        serializer = QualityControlSerializer(qc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@extend_schema(tags=['Evidence catalogs'])
class PatchDeleteQualityControlView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, EvidenceTypePermission]
    @extend_schema(
        description=_("[Protected | DeleteEvidenceType] Delete evidence type quality controls by id"),
        responses={200: CustomFieldSerializer(many=True)},
    )
    def delete(self, request, pk, qc_id):
        """Delete evidence type quality controls"""
        evidence_type = models.EvidenceType.objects.get(id=pk)
        models.QualityControl.objects.filter(id=qc_id, type=evidence_type.id).delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        description=_("[Protected |ChangeEvidenceType]Change evidence type quality controls by id"),
        request=AddPatchQualityControlSerializer,
        responses={200: CustomFieldSerializer},
    )
    def patch(self, request, pk, qc_id):
        """Update evidence type custom field"""
        evidence_type = models.EvidenceType.objects.get(id=pk)
        qc = models.QualityControl.objects.get(id=qc_id)

        # Update here
        body_serializer = AddPatchQualityControlSerializer(data=request.data)    
        body_serializer.is_valid(raise_exception=True)

        models.QualityControl.objects.filter(id=qc.id).update(**body_serializer.validated_data)

        # Return
        qc = models.QualityControl.objects.get(id=qc.id)
        serializer = QualityControlSerializer(qc)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
