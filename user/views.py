"""
Views frot he user API
"""
import logging
from drf_spectacular.utils import extend_schema

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
    """Custom permission for user handling"""
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
    """[Protected | AddUser] Create a new user in the system."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

class CreateTokenView(ObtainAuthToken):
    """[Public] Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """[Protected | IsAuthenticated] Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user

class ListUserView(generics.ListAPIView):
    """[Protected | ViewUser] List all users"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]
    queryset = get_user_model().objects.all().order_by('-id')

class RetrieveUserView(generics.RetrieveAPIView):
    """[Protected | ViewUser] Get user detail by id"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]
    queryset = get_user_model().objects.all()

class ListCreateUserGroupView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

    @extend_schema(
        responses={200: GroupSerializer(many=True)},
    )
    def get(self, request, pk):
        """[Protected | ViewUser] List user groups by user id"""
        user = get_user_model().objects.get(id=pk)
        serializer = GroupSerializer(user.groups.all(), many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=UpdateUserGroupSerializer,
        responses={200: GroupSerializer(many=True)},
    )
    def put(self, request, pk):
        """[Protected | ChangeUser] Set user groups ny user id"""
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