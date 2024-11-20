from django.http import JsonResponse
from category.models import Category, Subcategory
from store.permissions import IsSuperAdmin , IsOwnerOrSuperuser ,IsSuperUserOrReadOnly
from .serializers import   BrandSerializer, CategorySerializer, ProductSerializer , ProductImageSerializer, SampleProductImageSerializer, SubCategorySerializer  , ReviewSerializer, ToggleFavoriteSerializer
from .models import Brand, Product , ProductImage, Variation , ReviewRating
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets , permissions
from .forms import ProductForm , ProductImagesForm
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
import json
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated,AllowAny


class ProductListApi(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name','category__category__name', 'PRDBrand__name']

    def get_permissions(self):
        """
        Allow public access by default, but require authentication for 'is_favorites' filtering.
        """
        if self.request.query_params.get('is_favorites'):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        """
        Dynamically filter products based on query parameters.
        """
        queryset = Product.objects.all()
        is_favorites = self.request.query_params.get('is_favorites', None)

        if is_favorites:
            user = self.request.user
            if not user.is_authenticated:
                # If 'is_favorites' is requested but user is not authenticated, raise an exception.
                from rest_framework.exceptions import AuthenticationFailed
                raise AuthenticationFailed("Authentication is required to filter favorites.")
            queryset = queryset.filter(like=user)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Add additional metadata for favorited products.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Include only IDs of favorited products if authenticated
        favorites = []
        if request.user.is_authenticated:
            favorites = queryset.values_list('id', flat=True)

        return Response({
            "data": serializer.data,
            "favorites": list(favorites),  # Return as a list of IDs
        })


class ProductDetailApi(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'category__name', 'PRDBrand__name']  # Adjust fields as needed

class RecentProductListView(APIView):
    def get(self, request):
        # Fetch the latest 4 products by ordering with '-created_at'
        recent_products = Product.objects.all().order_by('-created_at')[:4]
        serializer = ProductSerializer(recent_products, many=True,context={'request':request})
        return Response(serializer.data)

# Create and Update Product View

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def create_product(request):
    # Process product form
    product_form = ProductForm(request.POST, request.FILES)
    print("before product_form.is_valid()")
    if product_form.is_valid():
        print("after product_form.is_valid()")
        product = product_form.save(commit=True)

        # Process product images
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

        # Process variations
        variations = request.data.get('variations', '[]')
        
        # Parse variations as JSON if it's a string
        if isinstance(variations, str):
            try:
                variations = json.loads(variations)
            except json.JSONDecodeError:
                return JsonResponse({'errors': 'Invalid JSON format for variations.'}, status=400)

        for variation_data in variations:
            variation_category = variation_data.get('variation_category')
            variation_value = variation_data.get('variation_value')
            
            # Ensure both category and value are provided
            if not variation_category or not variation_value:
                return JsonResponse(
                    {'errors': 'Both variation_category and variation_value are required.'},
                    status=400
                )

            # Create and associate the Variation instance with the Product
            Variation.objects.create(
                product=product,
                variation_category=variation_category,
                variation_value=variation_value
            )

        return JsonResponse({'success': True})
    
    else:
        print("error", product_form.errors, product_form.non_field_errors)
        return JsonResponse({'errors': product_form.errors}, status=400)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def update_product(request, id):
    try:
        # Get the existing product instance
        instance_product = Product.objects.get(id=id)

        # Update product fields
        product_form = ProductForm(request.POST, request.FILES, instance=instance_product)
        if product_form.is_valid():
            product_form.save()

            # Check if new images are provided
            if 'images' in request.FILES:
                # Delete existing images associated with the product
                instance_product.images.all().delete()

                # Add the new images
                product_images = request.FILES.getlist('images')
                for image in product_images:
                    product_image_form = ProductImagesForm({'product': instance_product.id}, {'image': image})
                    if product_image_form.is_valid():
                        product_image = product_image_form.save(commit=False)
                        product_image.product = instance_product  # Associate with the existing product
                        product_image.save()
                    else:
                        print("Error with image form:", product_image_form.errors)
                        return JsonResponse({'errors': product_image_form.errors}, status=400)

            # Process variations if provided
            variations = request.data.get('variations', '[]')

            # Parse variations as JSON if it's a string
            if isinstance(variations, str):
                try:
                    variations = json.loads(variations)
                except json.JSONDecodeError:
                    return JsonResponse({'errors': 'Invalid JSON format for variations.'}, status=400)

            # Clear existing variations (optional)
            instance_product.product_variation.all().delete()

            # Add new variations
            for variation_data in variations:
                variation_category = variation_data.get('variation_category')
                variation_value = variation_data.get('variation_value')

                # Ensure both category and value are provided
                if not variation_category or not variation_value:
                    return JsonResponse(
                        {'errors': 'Both variation_category and variation_value are required.'},
                        status=400
                    )

                # Create and associate the Variation instance with the Product
                Variation.objects.create(
                    product=instance_product,
                    variation_category=variation_category,
                    variation_value=variation_value
                )

            return JsonResponse({"success": True, "message": "Product updated successfully"})

        else:
            return JsonResponse({'errors': product_form.errors}, status=400)

    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found or you are not authorized to edit it"}, status=404)


# Delete Product View

class ProductDeleteView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [IsAdminUser]
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)

# Create Images
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

# List Images
class ProductImageListView(APIView):
    def get(self, request, product_id):
        product_images = ProductImage.objects.filter(product__id=product_id)
        serializer = ProductImageSerializer(product_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Update Images    
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
    
# Delete Images    
class ProductImageDeleteView(APIView):
    def delete(self, request, product_id, image_id):
        try:
            # Ensure the product image exists for the given product and image ID
            product_image = ProductImage.objects.get(product_id=product_id, id=image_id)
            product_image.delete()
            return Response({"detail": "Image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

# List all images        
class AllProductImagesView(generics.ListAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = SampleProductImageSerializer

# Category endpoints for dashboard
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperAdmin]  # Apply custom permission

# Subcategories endpoints for dashboard
class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsSuperAdmin]  # Apply custom permission

# Brands endpoints for dashboard
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def get_permissions(self):
        if self.action == 'list':
            # No authentication needed for listing
            return [permissions.AllowAny()]
        return [IsSuperUserOrReadOnly()]

# Review endpoints
class ReviewRatingViewSet(viewsets.ModelViewSet):
    queryset = ReviewRating.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if the user has already reviewed this product
        product_id = request.data.get("product")
        review = ReviewRating.objects.filter(user=request.user, product_id=product_id).first()
        
        if review:
            # If the review exists, update it
            serializer = self.get_serializer(review, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            # Otherwise, create a new review
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        # Automatically set the user field and IP address
        serializer.save(user=self.request.user, ip=self.get_client_ip())

    def perform_update(self, serializer):
        # Ensure the review can only be updated by the user who created it
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You cannot edit someone else's review.")
        serializer.save()

    def get_permissions(self):
        # Use custom permission for delete action
        if self.action == 'destroy':
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperuser]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        # Overriding destroy method to enforce the permission check
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_client_ip(self):
        # Get client IP address from the request
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Get the product by ID
        product = get_object_or_404(Product, pk=pk)

        # Toggle the favorite status
        if product.like.filter(id=request.user.id).exists():
            product.like.remove(request.user)
            is_favorite = False
        else:
            product.like.add(request.user)
            is_favorite = True

        # Get all favorites for the current user
        favorite_products = Product.objects.filter(like=request.user)
        count = favorite_products.count()

        # Serialize the favorite products
        product_serializer = ProductSerializer(favorite_products, many=True,context={'request':request})

        # Prepare the response
        response_data = {
            "is_favorite": is_favorite,
            "favorites_count": count,
            "favorites": product_serializer.data
        }

        return Response(response_data)