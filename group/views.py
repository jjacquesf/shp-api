from django.utils.translation import gettext as _

from django.shortcuts import render
from rest_framework import generics, authentication, permissions

from core import models

from group.serializers import (
    GroupSerializer
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