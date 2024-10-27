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
from .forms import ProductForm , ProductImagesForm
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
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def create_product(request):
    product_form = ProductForm(request.POST , request.FILES)
    print("before product_form.is_valid()")
    if product_form.is_valid():
        print("after product_form.is_valid()")
        product = product_form.save(commit=True)
        product_images = request.FILES.getlist('images')
        for image in product_images:
            product_image_form = ProductImagesForm({'product': product.id}, {'image': image})
            if product_image_form.is_valid():
                print("after product_image_form.is_valid()")
                product_image = product_image_form.save(commit=False)
                product_image.product = product  # Associate the product with the image
                product_image.save()
            else:
                print("Error with image form:", product_image_form.errors)
                return JsonResponse({'errors': product_image_form.errors}, status=400)
        return JsonResponse({'success':True})
    else:
        print("error",product_form.errors,product_form.non_field_errors)
        return JsonResponse({'errors':product_form.errors.as_json()},status=400)
    
@api_view(["PUT"]) 
@authentication_classes([])
@permission_classes([])
def update_product(request , id):
    try:
        instance_product = Product.objects.get(id=id)
        product_form = ProductForm(request.POST , request.FILES , instance=instance_product)
        if product_form.is_valid():
            product_form.save()

            if 'images' in request.FILES:
                product_images = request.FILES.getlist('images')
                for image in product_images:
                    product_image_form = ProductImagesForm({'product' : instance_product.id} , {'image' :image})
                    if product_image_form.is_valid():
                        product_image = product_image_form.save(commit=False)
                        product_image.product = instance_product
                        product_image.save()
                    else:
                        print("Error with image form:", product_image_form.errors)
                        return JsonResponse({'errors': product_image_form.errors}, status=400)
                return JsonResponse({"success":True,"message":"Product updated successfully"})
            else:
                return JsonResponse({'error':product_form.errors.as_json()},status = 400)
    except Product.DoesNotExist:
        return JsonResponse({"error":"Property not found or you are not authorized to edit it"},status=404)


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