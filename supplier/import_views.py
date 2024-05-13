# import xlrd
import re
from pyexcel_xlsx import get_data
from rest_framework.parsers import FileUploadParser


from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from django.utils.translation import gettext as _

from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework import views, authentication, permissions
from rest_framework.response import Response

from core import models


class ImportCatalogPermission(permissions.BasePermission):
    """Custom permission for user handling"""
    message = _('Requested action is not authorized')

    def has_permission(self, request, view):
        """Validate user permissions depending on the request method"""
        if request.method == 'POST':
            return request.user.has_perm('core.add_department')
    
        return False
    

@extend_schema(tags=['Catalogs'])
class ImportView(views.APIView):
    parser_classes = (FileUploadParser,)
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, 
                          ImportCatalogPermission
                          ]

    @extend_schema(
        description=_("[Protected | ImportSupplier] Import records"),
    )
    def post(self, request, filename, format=None):
        file = request.FILES['file']
        data = get_data(file)

        rows = data.get('Registros')
        messages = []
        if rows != None:
            if(len(rows) > 1):
                headers = rows.pop(0)
                for row in rows:
                    if len(row) >= 5:
                        id = None
                        if type(row[0]) is int:
                            id = row[0]
                        
                        is_active = False
                        if row[1] == 'Si':
                            is_active = True

                        name = row[2]
                        tax_id = row[3]
                        tax_name = row[4]

                        if id != None:
                            try:
                                instance = models.Supplier.objects.get(id=id)

                                instance.is_active = is_active
                                instance.name = name
                                instance.tax_id = tax_id
                                instance.tax_name = tax_name

                                instance.save()

                            except IntegrityError as e:
                                if re.search('name', str(e)):
                                    messages.append(f"Registro duplicado: {name}")

                                if re.search('tax_id', str(e)):
                                    messages.append(f"El RFC {tax_id} ya se encuentra asociado a otro registro")

                                if re.search('tax_name', str(e)):
                                    messages.append(f"La razón social {tax_name} ya se encuentra asociada a otro registro")
                        else:
                            try:
                                models.Supplier.objects.create(
                                    is_active=is_active,
                                    name=name,
                                    tax_id=tax_id,
                                    tax_name=tax_name,
                                )

                            except IntegrityError as e:
                                if re.search('name', str(e)):
                                    messages.append(f"Registro duplicado: {name}")

                                if re.search('tax_id', str(e)):
                                    messages.append(f"El RFC {tax_id} ya se encuentra asociado a otro registro")

                                if re.search('tax_name', str(e)):
                                    messages.append(f"La razón social {tax_name} ya se encuentra asociada a otro registro")
            else:
                messages.append('Debe especificar al menos un registro para crear o actualizar.')
        else:
            messages.append('El archivo debe incluir una hoja llamada: Registros')

        return Response({
            "success": True,
            "messages": messages
        })
        