from django.utils.translation import gettext as _

from django.shortcuts import render
from rest_framework import views, generics, authentication, permissions
from rest_framework.response import Response

from django.contrib.auth.models import Permission

from core import models

from group.serializers import (
    GroupSerializer,
    PermissionSerializer
)
class GroupPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the method"""
        # Use view.action for ViewSet 
        # Use request.method for APIView 

        if request.method == 'GET':
            return request.user.has_perm('core.view_customgroup') 

        if request.method == 'POST':
            return request.user.has_perm('core.add_customgroup')

        if request.method == 'UPDATE' or request.method == 'PATCH':
            return request.user.has_perm('core.change_customgroup') 

        if request.method == 'DELETE':
            return request.user.has_perm('core.delete_customgroup') 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

class ListCreateGroupView(generics.ListCreateAPIView):
    """List users"""
    serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, GroupPermission]
    queryset = models.CustomGroup.objects.all().order_by('-id')

class ManageGroupView(generics.RetrieveUpdateDestroyAPIView):
    """Destroy a new user in the system"""
    serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, GroupPermission]
    queryset = models.CustomGroup.objects.all()

class ListCreateGroupPermissionView(views.APIView):
    """List group permissions"""
    # serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, GroupPermission]

    # def get_queryset(self):
    #     return Permission.objects.all()
    #     # content_type = ContentType.objects.get_for_model(get_user_model())
    #     # content_type2 = ContentType.objects.get_for_model(models.CustomGroup)
    #     # return Permission.objects.filter(Q(content_type=content_type) | Q(content_type=content_type2))
    
    def get(self, request, pk):
        group = models.CustomGroup.objects.get(id=pk)
        serializer = PermissionSerializer(group.permissions.all(), many=True)
        return Response(serializer.data)