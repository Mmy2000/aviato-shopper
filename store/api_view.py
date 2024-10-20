from django.http import JsonResponse
from .serializers import   ProductSerializer
from .models import Product , ProductImage
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)


class ProductListApi(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

class ProductDetailApi(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

# Create and Update Product View
class ProductCreateUpdateView(APIView):
    def post(self, request):
        # Create Product
        product_serializer = ProductSerializer(data=request.data)
        if product_serializer.is_valid():
            product = product_serializer.save()

            # Handle images
            images_data = request.FILES.getlist('images')
            for image in images_data:
                ProductImage.objects.create(product=product, image=image)

            return Response(product_serializer.data, status=status.HTTP_201_CREATED)
        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # Update Product
        product = get_object_or_404(Product, pk=pk)
        product_serializer = ProductSerializer(product, data=request.data, partial=True)

        if product_serializer.is_valid():
            product = product_serializer.save()

            # Handle images
            images_data = request.FILES.getlist('images')
            for image in images_data:
                ProductImage.objects.create(product=product, image=image)

            return Response(product_serializer.data, status=status.HTTP_200_OK)
        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Product View
class ProductDeleteView(APIView):
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)
