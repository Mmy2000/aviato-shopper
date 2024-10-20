from rest_framework import viewsets
from .models import Product , ProductImage , Variation
from .serializers import ProductSerializer , ProductImageSerializer , VariationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsSuperAdmin  # Import the custom permission

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSuperAdmin]  # Apply the custom permission

    lookup_field = 'id'

    def perform_create(self, serializer):
        # Logic to handle creation, only accessible to super admins
        serializer.save()

    def perform_update(self, serializer):
        # Logic to handle update, only accessible to super admins
        serializer.save()

    def perform_destroy(self, instance):
        # Logic to handle delete, only accessible to super admins
        instance.delete()

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class VariationViewSet(viewsets.ModelViewSet):
    queryset = Variation.objects.all()
    serializer_class = VariationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]