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
        content_type2 = ContentType.objects.get_for_model(models.Group)
        content_type3 = ContentType.objects.get_for_model(models.Municipality)
        content_type4 = ContentType.objects.get_for_model(models.Institution)
        content_type5 = ContentType.objects.get_for_model(models.Dpe)
        content_type6 = ContentType.objects.get_for_model(models.Supplier)
        content_type7 = ContentType.objects.get_for_model(models.Department)
        content_type8 = ContentType.objects.get_for_model(models.Entity)
        content_type9 = ContentType.objects.get_for_model(models.StateOrg)
        content_type10 = ContentType.objects.get_for_model(models.SifUser)
        content_type11 = ContentType.objects.get_for_model(models.SianUser)
        content_type12 = ContentType.objects.get_for_model(models.EvidenceStatus)
        content_type13 = ContentType.objects.get_for_model(models.EvidenceType)
        content_type14 = ContentType.objects.get_for_model(models.CustomField)
        content_type15 = ContentType.objects.get_for_model(models.Evidence)
        content_type16 = ContentType.objects.get_for_model(models.QualityControl)
        content_type17 = ContentType.objects.get_for_model(models.EvidenceQualityControl)
        content_type18 = ContentType.objects.get_for_model(models.EvidenceComment)
        content_type19 = ContentType.objects.get_for_model(models.Division)
        content_type20 = ContentType.objects.get_for_model(models.Theme)
        
        bd_q = Q(content_type=content_type) | Q(content_type=content_type2) | Q(content_type=content_type3) | Q(content_type=content_type4) | Q(content_type=content_type5) | Q(content_type=content_type6) | Q(content_type=content_type7) | Q(content_type=content_type8) | Q(content_type=content_type9) | Q(content_type=content_type10) | Q(content_type=content_type11) | Q(content_type=content_type12) | Q(content_type=content_type13) | Q(content_type=content_type14) | Q(content_type=content_type15) | Q(content_type=content_type16) | Q(content_type=content_type17) | Q(content_type=content_type18)  | Q(content_type=content_type19) | Q(content_type=content_type20)

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PermissionQuerySet().business_domain()