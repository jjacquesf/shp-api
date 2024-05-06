from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q
from django.utils.translation import gettext as _

from django.shortcuts import render
from rest_framework import views, generics, authentication, permissions
from rest_framework.response import Response
from rest_framework import serializers

from django.contrib.auth.models import Permission

from core import models

from group.serializers import (
    GroupSerializer,
    UpdateGroupPermissionSerializer
)

from permission.serializers import (
    PermissionSerializer
)

from permission.views import (
    PermissionQuerySet
)

class GroupPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""
        # Use view.action for ViewSet 
        # Use request.method for APIView 

        if request.method == 'GET':
            return request.user.has_perm('auth.view_group') 

        if request.method == 'POST':
            return request.user.has_perm('auth.add_group')

        if request.method == 'PUT' or request.method == 'PATCH':
            return request.user.has_perm('auth.change_group') 

        if request.method == 'DELETE':
            return request.user.has_perm('auth.delete_group') 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True
@extend_schema(tags=[_('Groups and Permissions')])
@extend_schema_view(
    get=extend_schema(description=_("[Protected | ViewGroup] List all groups")),
    post=extend_schema(description=_("[Protected | AddGroup] Add a group")),
)
class ListCreateGroupView(generics.ListCreateAPIView):
    """[Protected | ViewGroup] List groups"""
    serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, GroupPermission]
    queryset = models.CustomGroup.objects.all().order_by('-id')

@extend_schema(tags=[_('Groups and Permissions')])
@extend_schema_view(
    get=extend_schema(description=_("[Protected | ViewGroup] Get group by id")),
    put=extend_schema(description=_("[Protected | ChangeGroup] Update group by id")),
    patch=extend_schema(description=_("[Protected | ChangeGroup] Patch group by id")),
    delete=extend_schema(description=_("[Protected | DeleteGroup] Delete group by id")),
)
class ManageGroupView(generics.RetrieveUpdateDestroyAPIView):
    # """Destroy a new user in the system"""
    serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, GroupPermission]
    queryset = models.CustomGroup.objects.all()
    
    # @extend_schema(
    #     description=_("Get group object by id)"
    # )
    # def retrieve(request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """Destroy a custom field"""
        if(instance.user_set.count()):
            raise serializers.ValidationError(_('No se puede eliminar porque hay usuarios asigandos a este grupo.'))
        
        instance.delete()



@extend_schema(tags=[_('Groups and Permissions')])
@extend_schema_view(
    get=extend_schema(
        description=_("[Protected | ViewGroup] Get permissions by group id"),
        responses={200: PermissionSerializer(many=True)},
    ),
    put=extend_schema(
        description=_("[Protected | ChangeGroup] Update group permissions by group id"),
        request=UpdateGroupPermissionSerializer,
        responses={200: PermissionSerializer(many=True)},
    ),
)
class ListCreateGroupPermissionView(views.APIView):
    """List group permissions"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, GroupPermission]

    def get(self, request, pk):
        group = models.CustomGroup.objects.get(id=pk)
        serializer = PermissionSerializer(group.permissions.all(), many=True)
        return Response(serializer.data)
    
    def put(self, request, pk):
        body_serializer = UpdateGroupPermissionSerializer(request.data)

        cond = Q()
        for perm in body_serializer.data['permissions']:
            cond |= Q(codename=perm)

        # Get allowed permissions only
        perms = PermissionQuerySet().business_domain(cond)

        group = models.CustomGroup.objects.get(id=pk)
        group.permissions.set(perms)

        serializer = PermissionSerializer(group.permissions.all(), many=True)
        return Response(serializer.data)