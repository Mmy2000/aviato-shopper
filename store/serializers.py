from rest_framework import serializers
from .models import Product, ProductImage, Brand , Variation
from category.models import Category , Subcategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields ='__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Subcategory
        fields = "__all__"

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ['id', 'variation_category', 'variation_value', 'is_active', 'created_at']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = SubCategorySerializer(read_only=True)
    PRDBrand = BrandSerializer(read_only=True)
    variations = VariationSerializer(source='product_variation', many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'stock', 'price', 'description', 'created_at', 'modified_date', 'slug', 'views', 'is_available', 'on_sale', 'PRDBrand','variations', 'like', 'category', 'images', 'avr_review', 'count_review']


class SampleProductImageSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = ProductImage
        fields = ['id', 'image','product']