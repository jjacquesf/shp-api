# import xlrd
from pyexcel_xlsx import get_data
from rest_framework.parsers import FileUploadParser


from django.core.exceptions import ObjectDoesNotExist

from department.views import DepartmentPermission
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
        description=_("[Protected | ImportDepartment] Import records"),
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

                        parent_name = None
                        if len(row) > 3:
                            parent_name = row[3]
                        parent = None
                        if parent_name != None:
                            parent = models.Department.objects.filter(name=parent_name)
                            if len(parent):
                                parent = parent[0]

                        if id != None:
                            try:
                                instance = models.Department.objects.get(id=id)

                                level = 0
                                if parent != None:
                                    if parent.id == instance.id:
                                        parent = None
                                    level = parent.level + 1

                                instance.is_active = is_active
                                instance.name = name
                                instance.parent = parent
                                instance.level = level

                                instance.save()

                            except ObjectDoesNotExist:
                                messages.append(f"No existe un registro con el id: {id}")
                                pass
                        else:
                            level = 0
                            if parent != None:
                                level = parent.level + 1

                            models.Department.objects.create(
                                is_active=is_active,
                                name=name,
                                level=level,
                                parent=parent
                            )
            else:
                messages.append('Debe especificar al menos un registro para crear o actualizar.')
        else:
            messages.append('El archivo debe incluir una hoja llamada: Registros')

        return Response({
            "success": True,
            "messages": messages
        })
        