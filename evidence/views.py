"""
Views frot he evidence API
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

from evidence.serializers import (
    CreateEvidenceSerializer,
    EvidenceSerializer,
    serialize_evidence
)

class EvidencePermission(permissions.BasePermission):
    """Custom permission for evidence handling"""
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate evidence permissions depending on the request method"""
        # Use view.action for ViewSet 
        # Use request.method for APIView 

        if request.method == 'GET':
            return request.user.has_perm('core.view_evidence') 

        if request.method == 'POST':
            return request.user.has_perm('core.add_evidence')

        if request.method == 'PATCH':
            return request.user.has_perm('core.change_evidence') 

        if request.method == 'DELETE':
            return request.user.has_perm('core.delete_evidence') 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        return True
   
@extend_schema(tags=['Evidence management'])
class ListEvidence(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, EvidencePermission]

    @extend_schema(
        description=_("[Protected | ViewEvidence] List all evidences"),
        responses={200: EvidenceSerializer(many=True)},
    )
    def get(self, request):
        queryset = models.Evidence.objects.filter()
        
        status = request.query_params.get('status')
        if status != None:
            queryset = queryset.filter(status=status)

        records = queryset.filter(parent=None).order_by('-id')
        result = []
        for record in records:
            serializer = serialize_evidence(record)
            result.append(serializer.data)

        return Response(result)
    
@extend_schema(tags=['Evidence management'])
@extend_schema(description=_("[Protected | AddEvidence] Create a new evidence"))
class CreateEvidenceView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, EvidencePermission]

    @extend_schema(
        description=_("[Protected | ChangeUser] Set user groups ny user id"),
        request=CreateEvidenceSerializer,
        responses={200: EvidenceSerializer},
    )
    def post(self, request):
        serializer = CreateEvidenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if("password" not in request.data):
            return Response({"password": [_("Password is required for user creation")]}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=serializer.validated_data['email'])
        if len(user) != 0:
            return Response({"email": [_("User already exists")]}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
