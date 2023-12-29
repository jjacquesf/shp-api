from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


from rest_framework import generics, authentication, permissions
from django.contrib.contenttypes.models import ContentType

from permission.serializers import (
    PermissionSerializer
)

from django.contrib.auth.models import Permission
from core import models
class ViewPermissionsPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        return request.user.has_perm('auth.view_permission')

class ListPermissionView(generics.ListAPIView):
    """List users"""
    serializer_class = PermissionSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, ViewPermissionsPermission]

    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(get_user_model())
        content_type2 = ContentType.objects.get_for_model(models.CustomGroup)
        return Permission.objects.filter(Q(content_type=content_type) | Q(content_type=content_type2))
