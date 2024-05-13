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
            return request.user.has_perm('core.add_stateorg')
    
        return False
    

@extend_schema(tags=['Catalogs'])
class ImportView(views.APIView):
    parser_classes = (FileUploadParser,)
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, 
                          ImportCatalogPermission
                          ]

    @extend_schema(
        description=_("[Protected | ImportSifUser] Import records"),
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
                    if len(row) >= 3:
                        id = None
                        if type(row[0]) is int:
                            id = row[0]
                        
                        is_active = False
                        if row[1] == 'Si':
                            is_active = True

                        name = row[2]

                        stateorg_name = None
                        if len(row) > 3:
                            stateorg_name = row[3]
                        stateorg = None
                        if stateorg_name != None:
                            stateorg = models.StateOrg.objects.filter(name=stateorg_name)
                            if len(stateorg):
                                stateorg = stateorg[0]
                            else:
                                messages.append(f"No se encontró la dependencia estatal: {stateorg_name}")
                                continue

                        if id != None:
                            try:
                                instance = models.SifUser.objects.get(id=id)

                                level = 0
                                if stateorg != None:
                                    if stateorg.id == instance.id:
                                        stateorg = None
                                    level = stateorg.level + 1

                                instance.is_active = is_active
                                instance.name = name
                                instance.stateorg = stateorg
                                instance.level = level

                                instance.save()

                            except ObjectDoesNotExist:
                                messages.append(f"No existe un registro con el id: {id}")
                            except IntegrityError as e:
                                if re.search('stateorg_id', str(e)):
                                    messages.append(f"Organización estatal es obligatoria")

                                if re.search('name', str(e)):
                                    messages.append(f"Registro duplicado: {name}")
                        else:
                            level = 0
                            if stateorg != None:
                                level = stateorg.level + 1

                            try:
                                models.SifUser.objects.create(
                                    is_active=is_active,
                                    name=name,
                                    level=level,
                                    stateorg=stateorg
                                )
                            except IntegrityError as e:
                                if re.search('stateorg_id', str(e)):
                                    messages.append(f"Organización estatal es obligatoria")

                                if re.search('name', str(e)):
                                    messages.append(f"Registro duplicado: {name}")
            else:
                messages.append('Debe especificar al menos un registro para crear o actualizar.')
        else:
            messages.append('El archivo debe incluir una hoja llamada: Registros')

        return Response({
            "success": True,
            "messages": messages
        })
        