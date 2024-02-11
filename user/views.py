"""
Views frot he user API
"""
import logging
from rest_framework import status

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
    UpdateUserGroupSerializer,
    AuthTokenSerializer,
    UserProfileSerializer,
    serialize_user_profile
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
    
@extend_schema(tags=['Auth'])
@extend_schema(description=_("[Public] Create a new auth token for user"))
class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

@extend_schema(tags=['Auth'])
@extend_schema(description=_("[Protected | IsAuthenticated] Manage the authenticated user"))
class SelfManageUserView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description=_("[Protected | IsAuthenticated] Get user self profile"),
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        user = self.request.user
        # profile = models.Profile.objects.get(user=user)
        # serializer = UserProfileSerializer({
        #     "name": user.name,
        #     "email": user.email,
        #     "password": user.password,
        #     "job_position": profile.job_position
        # })
        serializer = serialize_user_profile(user)
        return Response(serializer.data)
    
    @extend_schema(
        description=_("[Protected | IsAuthenticated] Update self user profile"),
        request=UpdateUserGroupSerializer,
        responses={200: GroupSerializer(many=True)},
    )
    def put(self, request):
        """Update and return user"""
        user = get_user_model().objects.get(id=self.request.user.id)
        # profile = models.Profile.objects.get(user=user)

        serializer = UserProfileSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        
        user.refresh_from_db()
        # profile.refresh_from_db()

        # upd_serializer = UserProfileSerializer({
        #     "name": user.name,
        #     "email": user.email,
        #     "password": user.password,
        #     "job_position": profile.job_position
        # })

        upd_serializer = serialize_user_profile(user)

        return Response(upd_serializer.data)
    
@extend_schema(tags=['User management'])
class ListUserView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

    @extend_schema(
        description=_("[Protected | ViewUser] List all users"),
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        users = get_user_model().objects.filter(is_superuser=False).order_by('-id')
        result = []
        for user in users:
            # profile = models.Profile.objects.get(user=user)
            # serializer = UserProfileSerializer({
            #     "name": user.name,
            #     "email": user.email,
            #     "job_position": profile.job_position
            # })
            serializer = serialize_user_profile(user)
            result.append(serializer.data)

        return Response(result)
@extend_schema(tags=['User management'])
class ManageUserView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

    @extend_schema(
        description=_("[Protected | ViewUser] Get user profile by id"),
        responses={200: UserProfileSerializer},
    )
    def get(self, request, pk):
        user = get_user_model().objects.get(id=pk)
        # profile = models.Profile.objects.get(user=user)
        # serializer = UserProfileSerializer({
        #     "name": user.name,
        #     "email": user.email,
        #     "job_position": profile.job_position
        # })
        serializer = serialize_user_profile(user)
        return Response(serializer.data)
    
    @extend_schema(
        description=_("[Protected | ChangeUser] Update user profile by id"),
        request=UpdateUserGroupSerializer,
        responses={200: GroupSerializer(many=True)},
    )
    def put(self, request, pk):
        """Update and return user"""
        user = get_user_model().objects.get(id=pk)
        profile = models.Profile.objects.get(user=user)

        serializer = UserProfileSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        
        user.refresh_from_db()
        profile.refresh_from_db()

        # upd_serializer = UserProfileSerializer({
        #     "name": user.name,
        #     "email": user.email,
        #     "job_position": profile.job_position
        # })
        upd_serializer = serialize_user_profile(user)
        return Response(upd_serializer.data)

@extend_schema(tags=['User management'])
@extend_schema(description=_("[Protected | AddUser] Create a new user in the system"))
class CreateUserView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

    @extend_schema(
        description=_("[Protected | ChangeUser] Set user groups ny user id"),
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
    )
    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if("password" not in request.data):
            return Response({"password": [_("Password is required for user creation")]}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=serializer.validated_data['email'])
        if len(user) != 0:
            return Response({"email": [_("User already exists")]}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(tags=['User management'])
class ListCreateUserGroupView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, UserPermission]

    @extend_schema(
        description=_("[Protected | ViewUser] List user groups by user id"),
        responses={200: GroupSerializer(many=True)},
    )
    def get(self, request, pk):
        user = get_user_model().objects.get(id=pk)
        serializer = GroupSerializer(user.groups.all(), many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description=_("[Protected | ChangeUser] Set user groups ny user id"),
        request=UpdateUserGroupSerializer,
        responses={200: GroupSerializer(many=True)},
    )
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