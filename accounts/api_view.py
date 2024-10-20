from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView 
from .serializers import RegisterSerializer,LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": {
                    "email": data['user'].email,
                    "username": data['user'].username,
                    'is_admin':data['user'].is_admin,
                    'is_staff':data['user'].is_staff,
                    'is_superadmin':data['user'].is_superadmin,
                },
                "refresh": data['refresh'],
                "access": data['access']
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_admin':user.is_admin,
                'is_staff':user.is_staff,
                'is_superadmin':user.is_superadmin,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)