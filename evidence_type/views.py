"""
Views frot he evience types API
"""
from drf_spectacular.utils import extend_schema

from django.utils.translation import gettext as _

from rest_framework import views, authentication, permissions
from rest_framework.response import Response


from core import models

from evidence_type.serializers import (
    EvidenceTypeSerializer
)

@extend_schema(tags=['Evidence management'])
class ListEvidenceTypeView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description=_("[Protected | IsAuthenticated] List all evidence types"),
        responses={200: EvidenceTypeSerializer(many=True)},
    )
    def get(self, request):
        rows = models.EvidenceType.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceTypeSerializer(rows, many=True)
        return Response(serializer.data)

