# import xlrd
from django.utils.translation import gettext as _

from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework import views
from rest_framework.response import Response

from core import models
    

@extend_schema(tags=['Theme'])
class ColorsView(views.APIView):
    @extend_schema(
        description=_("[Public]"),
    )
    def get(self, request):
        theme = models.Theme.objects.filter().first()
        return Response({
            "primary": theme.primary,
            "secondary": theme.secondary,
            "terciary": theme.terciary,
            "quaternary": theme.quaternary,
        })
        