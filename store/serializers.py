from rest_framework import serializers

from order.models import OrderProduct
from .models import Product, ProductImage, Brand , Variation,ReviewRating
from category.models import Category , Subcategory
from accounts.models import User , Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image', 'about', 'country', 'address_line_1', 'address_line_2', 'headline', 'city', 'full_address']
        read_only_fields = ['full_address']  # Makes `full_address` a read-only field

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Nested serializer

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'full_name', 'profile']
        read_only_fields = ['full_name']  # Makes `full_name` a read-only field

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields ='__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Allow category_id input

    class Meta:
        model = Subcategory
        fields = "__all__"
    
    def to_representation(self, instance):
        """
        Override this method to display category details in the response,
        while still allowing category_id to be passed on input.
        """
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data  # Nest the full category details
        return representation

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ['id', 'variation_category', 'variation_value', 'is_active', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ReviewRating
        fields = ['id', 'user', 'product', 'subject', 'review', 'rating', 'ip', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = SubCategorySerializer(read_only=True)
    PRDBrand = BrandSerializer(read_only=True)
    variations = VariationSerializer(source='product_variation', many=True, read_only=True)
    reviewrating = ReviewSerializer(many=True, read_only=True)
    
    # New fields for color and size variations
    color_variations = serializers.SerializerMethodField()
    size_variations = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = [
            'id', 'name', 'image', 'price', 'description', 'slug', 'on_sale', 'like', 
            'category', 'PRDBrand', 'variations', 'images', 'reviewrating', 
            'avr_review', 'count_review', 'color_variations', 'size_variations'
        ]

    def get_color_variations(self, obj):
        color_variations = obj.product_variation.filter(variation_category='color', is_active=True)
        return VariationSerializer(color_variations, many=True).data

    def get_size_variations(self, obj):
        size_variations = obj.product_variation.filter(variation_category='size', is_active=True)
        return VariationSerializer(size_variations, many=True).data
    
    
    

class SampleProductImageSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = ProductImage
        fields = ['id', 'image','product']

class ToggleFavoriteSerializer(serializers.Serializer):
    is_favorite = serializers.BooleanField()