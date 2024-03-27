from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateFileUploadSerializer, FileUploadSerializer

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
