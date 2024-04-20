from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateFileUploadSerializer, FileUploadSerializer

from core import models

import os
from django.conf import settings
from django.http import HttpResponse, Http404
import mimetypes

class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateFileUploadSerializer

        return self.serializer_class

    
    def post(self, request, *args, **kwargs):
        serializer = CreateFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            data = {
                **serializer.validated_data,
                'owner': request.user.id
            }

            s = FileUploadSerializer(data=data)
            if s.is_valid():
                s.save()
                return Response(
                    s.data,
                    status=status.HTTP_201_CREATED
                )
            
            return Response(
                s.errors,
                status=status.HTTP_400_BAD_REQUEST
            )   
        
class FileDownloadAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        model = models.UploadedFile.objects.get(id=pk)
        file_path = os.path.join(model.file.path)
        if os.path.exists(file_path):
            mt = mimetypes.guess_type(file_path)
            if mt:
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type=mt[0])
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    return response
        raise Http404
