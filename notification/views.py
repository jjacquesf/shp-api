from django.shortcuts import render

# Create your views here.
"""
Views fro the notification APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core import models

from notification.serializers import (
    NotificationSerializer,
    CreateNotificationSerializer,
    UpdateNotificationSerializer
)

@extend_schema(tags=['Notifications'])
@extend_schema_view(
    list=extend_schema(
        description=_('[Protected | IsAuthenticayed] List notifications'),
        parameters=[
            OpenApiParameter(
                'all',
                OpenApiTypes.STR,
                required=False,
                description=_('Either "true" or "false" depending on the desired query. Default: "false"')
            ),
            OpenApiParameter(
                'evidence',
                OpenApiTypes.INT,
                required=False,
                description=_('Evidence id filter value')
            ),
            OpenApiParameter(
                'user',
                OpenApiTypes.INT,
                required=False,
                description=_('User id filter value')
            ),
        ]
    ),
    create=extend_schema(
        description=_('[Protected | IsAuthenticayed] Add an notification')
    ),
    partial_update=extend_schema(
        description=_('[Protected | IsAuthenticayed] Partial update an notification by id')
    ),
)
class NotificationViewSet(viewsets.ModelViewSet):
    """Viewset for manage notification APIs."""
    serializer_class = NotificationSerializer
    queryset = models.Notification.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):
        if self.action == 'create':
            return CreateNotificationSerializer
        
        if self.action == 'partial_update':
            return UpdateNotificationSerializer

        return self.serializer_class

    def get_queryset(self):
        """Retrieve notification sorted by name"""
        all = self.request.query_params.get('all')

        # Filter objects by active status
        queryset = self.queryset
        queryset = queryset.filter(user=self.request.user)

        if (self.request.method == 'GET' or self.request.method == 'PATCH') and all == None:
            queryset = queryset.filter(opened=False)
        else:
            queryset = queryset.filter(opened=True)
        evidence = self.request.query_params.get('evidence')
        if evidence != None:
            queryset = queryset.filter(evidence=evidence)

        return queryset.order_by('-id')

    def perform_create(self, serializer):
        """Create a new notification"""

        payload={'user': self.request.user.id}
        payload.update(serializer.data)

        s = CreateNotificationSerializer(data=payload)
        s.is_valid(raise_exception=True)
        return s.save()
    