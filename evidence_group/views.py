"""
Views frot he evience groups API
"""
from drf_spectacular.utils import extend_schema

from django.utils.translation import gettext as _

from rest_framework import views, authentication, permissions
from rest_framework.response import Response


from core import models

from evidence_group.serializers import (
    EvidenceGroupSerializer
)

@extend_schema(tags=['Evidence catalogs'])
class ListEvidenceGroupView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description=_("[Protected | IsAuthenticated] List all evidence groups"),
        responses={200: EvidenceGroupSerializer(many=True)},
    )
    def get(self, request):
        rows = models.EvidenceGroup.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceGroupSerializer(rows, many=True)
        return Response(serializer.data)

