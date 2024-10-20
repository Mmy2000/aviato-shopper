from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response({
                "status": "success",
                "message": "User registered successfully.",
                "data": {
                    "user_info": {
                        "email": data['user'].email,
                        "username": data['user'].username,
                        "is_admin": data['user'].is_admin,
                        "is_staff": data['user'].is_staff,
                        "is_superadmin": data['user'].is_superadmin,
                    },
                    "tokens": {
                        "refresh_token": data['refresh'],
                        "access_token": data['access'],
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Registration failed. Please check the details provided.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Login successful.",
                "data": {
                    "tokens": {
                        "refresh_token": str(refresh),
                        "access_token": str(refresh.access_token),
                    },
                    "user_info": {
                        "is_admin": user.is_admin,
                        "is_staff": user.is_staff,
                        "is_superadmin": user.is_superadmin,
                    }
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Login failed. Invalid credentials.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
