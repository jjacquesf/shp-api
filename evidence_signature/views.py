"""
Views fro the evidence status APIs
"""
from drf_spectacular.utils import extend_schema, extend_schema_view


from django.utils.translation import gettext as _

from evidence.serializers import EvidenceSignatureSerializer, UpdateEvidenceSignatureSerializer
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core import models


class EvidenceSignaturePermission(permissions.BasePermission):
    message = _('Requested action is not authorized')

    # def has_permission(self, request, view):
    #     """Validate user permissions depending on the request method"""

    #     if view.action == 'retrieve':
    #         return request.user.has_perm('core.view_evidencesignature') 

    #     if view.action == 'partial_update':
    #         return request.user.has_perm('core.change_evidencesignature') 

    #     return False
    
    def has_object_permission(self, request, view, obj):
        """Validate user access to a specific object if necessary"""
        if request.user.has_perm('core.change_evidencesignature'):
            return True
    
        if request.user.has_perm('core.manage_evidence') and request.user.profile.division.id == obj.evidence.owner.profile.division.id:
            return True
        
        if request.user.has_perm('core.work_evidence') and request.user.id == obj.user.id:
            return True

        return False


@extend_schema(tags=['Evidence catalogs'])
@extend_schema_view(
   update=extend_schema(
        description=_('[Protected | ChangeEvidenceSignature] Replace an evidence signature control by id')
    ),
)
class EvidenceSignatureViewSet(viewsets.ModelViewSet):
    """Viewset for manage evidence status APIs."""
    serializer_class = EvidenceSignatureSerializer
    queryset = models.EvidenceSignature.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, EvidenceSignaturePermission]

    def get_queryset(self):
        """Retrieve evidence status sorted by name"""

        queryset = self.queryset
        return queryset
    
    def get_serializer_class(self):        
        if self.request.method == 'PATCH':
            return UpdateEvidenceSignatureSerializer

        return self.serializer_class