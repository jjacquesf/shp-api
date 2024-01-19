"""
Views frot he evience types API
"""
from drf_spectacular.utils import extend_schema

from django.utils.translation import gettext as _

from rest_framework import views, authentication, permissions
from rest_framework.response import Response


from core import models

from evidence_stage.serializers import (
    EvidenceStageSerializer
)

@extend_schema(tags=['Evidence catalogs'])
class ListEvidenceStageView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description=_("[Protected | IsAuthenticated] List all evidence stages"),
        responses={200: EvidenceStageSerializer(many=True)},
    )
    def get(self, request):
        rows = models.EvidenceStage.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceStageSerializer(rows, many=True)
        return Response(serializer.data)

