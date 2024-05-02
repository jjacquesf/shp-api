from rest_framework.response import Response
from rest_framework import views
from django.contrib.auth import get_user_model

from user.serializers import ResetPasswordRequestSerializer, ResetPasswordSerializer
from core import models
from django.utils.crypto import get_random_string

class ResetPasswordView(views.APIView):
    
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        user = get_user_model().objects.filter(email=email)

        if len(user) == 1:
            token = get_random_string(length=32)
            models.ResetPassword.objects.create(
                user=user[0],
                token=token
            )

        return Response({
            "success": True
        })
    
    def patch(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get('token')
        password = serializer.validated_data.get('password')
        reset_request = models.ResetPassword.objects.filter(token=token, used=False)

        if len(reset_request) == 1:
            reset_request[0].user.set_password(password)
            reset_request[0].used = True
            reset_request[0].save()
            return Response({
                "success": True
            })
        
        return Response({
            "success": False
        })