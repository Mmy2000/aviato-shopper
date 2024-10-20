from django.http import JsonResponse

from category.models import Category, Subcategory
from store.permissions import IsSuperAdmin
from .serializers import   CategorySerializer, ProductSerializer , ProductImageSerializer, SampleProductImageSerializer, SubCategorySerializer
from .models import Product , ProductImage
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets



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

class ProductImageCreateView(APIView):
    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        images = request.FILES.getlist('images')  # Get list of images from request
        image_objects = []

        for image in images:
            image_data = {'image': image}
            serializer = ProductImageSerializer(data=image_data)
            if serializer.is_valid():
                product_image = serializer.save(product=product)
                image_objects.append(product_image)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(ProductImageSerializer(image_objects, many=True).data, status=status.HTTP_201_CREATED)

class ProductImageListView(APIView):
    def get(self, request, product_id):
        product_images = ProductImage.objects.filter(product__id=product_id)
        serializer = ProductImageSerializer(product_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProductImageUpdateView(APIView):
    def put(self, request, product_id, image_id):
        try:
            # Fetch the image by product_id and image_id
            product_image = ProductImage.objects.get(product_id=product_id, id=image_id)
        except ProductImage.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Deserialize and validate the data (update the image)
        serializer = ProductImageSerializer(product_image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductImageDeleteView(APIView):
    def delete(self, request, product_id, image_id):
        try:
            # Ensure the product image exists for the given product and image ID
            product_image = ProductImage.objects.get(product_id=product_id, id=image_id)
            product_image.delete()
            return Response({"detail": "Image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)
        
class AllProductImagesView(generics.ListAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = SampleProductImageSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperAdmin]  # Apply custom permission

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsSuperAdmin]  # Apply custom permission