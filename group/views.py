from django.shortcuts import render
from rest_framework import generics, authentication, permissions

from core import models

from group.serializers import (
    GroupSerializer
)

class ViewGroupsPermission(permissions.BasePermission):
    message = 'Sorry view groups is not permitted'

    def has_permission(self, request, view):
        return request.user.has_perm('core.view_customgroup')
    
class AddGroupsPermission(permissions.BasePermission):
    message = 'Sorry change groups is not permitted'

    def has_permission(self, request, view):
        return request.user.has_perm('core.add_user')

class ChangeGroupsPermission(permissions.BasePermission):
    message = 'Sorry change groups is not permitted'

    def has_permission(self, request, view):
        return request.user.has_perm('core.change_user') 
    
class ListGroupView(generics.ListAPIView):
    """List users"""
    serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, ViewGroupsPermission]
    queryset = models.CustomGroup.objects.all().order_by('-id')

class CreateGroupView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, AddGroupsPermission]

