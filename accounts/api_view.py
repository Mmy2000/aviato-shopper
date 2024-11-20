from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order
from store.models import Product
from store.serializers import ProductSerializer
from .serializers import OrderSerializer, RegisterSerializer, LoginSerializer , ProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions
from . models import Profile
from rest_framework.permissions import IsAuthenticated


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

class ProfileDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Fetch and return the profile associated with the authenticated user
        return Profile.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        # Return custom response with HTTP 200 status
        return Response(
            {
                "message": "Profile updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class FavoriteProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        products = Product.objects.filter(like=user)  # Assuming 'like' is a ManyToManyField
        serializer = ProductSerializer(products, many=True,context={'request':request})
        return Response(serializer.data)
    
class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(user_orders,context={'request':request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(user=request.user, id=order_id)
            serializer = OrderSerializer(order,context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )