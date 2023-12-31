"""
Views frot he user API
"""
import logging
from django.db.models import Q
from django.utils.translation import gettext as _

from rest_framework import views, generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from core import models

from user.serializers import (
    UserSerializer,
    UpdateUserGroupSerializer,
    AuthTokenSerializer
)

from group.serializers import (
    GroupSerializer,
)


class UserPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""
        # Use view.action for ViewSet 
        # Use request.method for APIView 

        if request.method == 'GET':
            return request.user.has_perm('core.view_user') 

        if request.method == 'POST':
            return request.user.has_perm('core.add_user')

        if request.method == 'PUT' or request.method == 'PATCH':
            return request.user.has_perm('core.change_user') 

        if request.method == 'DELETE':
            return request.user.has_perm('core.delete_user') 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user

class ListUserView(generics.ListAPIView):
    """List users"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]
    queryset = get_user_model().objects.all().order_by('-id')

class RetrieveUserView(generics.RetrieveAPIView):
    """Get user detail"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]
    queryset = get_user_model().objects.all()

class ListCreateUserGroupView(views.APIView):
    """List user groups"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

    def get(self, request, pk):
        user = get_user_model().objects.get(id=pk)
        serializer = GroupSerializer(user.groups.all(), many=True)
        return Response(serializer.data)
    
    def put(self, request, pk):
        body_serializer = UpdateUserGroupSerializer(request.data)

        cond = Q()
        for group in body_serializer.data['groups']:
            cond |= Q(id=group)

        # Get allowed permissions only
        perms = models.CustomGroup.objects.filter(cond)

        user = get_user_model().objects.get(id=pk)
        user.groups.set(perms)

        serializer = GroupSerializer(user.groups.all(), many=True)
        return Response(serializer.data)