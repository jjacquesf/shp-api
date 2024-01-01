from drf_spectacular.utils import extend_schema

from django.db.models import Q
from django.db.models import query
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


from rest_framework import generics, authentication, permissions
from django.contrib.contenttypes.models import ContentType

from permission.serializers import (
    PermissionSerializer
)

from django.contrib.auth.models import Permission
from core import models

class PermissionQuerySet(query.QuerySet):
    """Permission Queryset"""

    def business_domain(self, additional_cond = Q()):
        """Queryset fro business domain permissions"""
        content_type = ContentType.objects.get_for_model(get_user_model())
        content_type2 = ContentType.objects.get_for_model(models.CustomGroup)
        bd_q = Q(content_type=content_type) | Q(content_type=content_type2)

        return Permission.objects.filter(bd_q & additional_cond)

class ViewPermissionsPermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        return request.user.has_perm('auth.view_permission')

@extend_schema(tags=['Groups and Permissions'])
@extend_schema(description=_("[Protected | ViewPermission] List all permissions"))
class ListPermissionView(generics.ListAPIView):
    serializer_class = PermissionSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, ViewPermissionsPermission]

    def get_queryset(self):
        return PermissionQuerySet().business_domain()