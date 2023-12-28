from django.shortcuts import render
from rest_framework import generics, authentication, permissions

from core import models

from group.serializers import (
    GroupSerializer
)

class ViewGroupsPermission(permissions.BasePermission):
    message = 'Sorry Group is not permitted'

    def has_permission(self, request, view):
        return request.user.has_perm('core.view_customgroup')
    
class ListGroupView(generics.ListAPIView):
    """List users"""
    serializer_class = GroupSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, ViewGroupsPermission]
    queryset = models.CustomGroup.objects.all().order_by('-id')
