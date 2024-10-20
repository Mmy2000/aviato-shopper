from rest_framework import serializers
from .models import Product, ProductImage, Variation

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ['id', 'variation_category', 'variation_value', 'is_active']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    product_variation = VariationSerializer(many=True, read_only=True)
    avr_review = serializers.ReadOnlyField()
    count_review = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'image', 'stock', 'price', 'description', 'created_at', 
            'modified_date', 'slug', 'views', 'is_available', 'on_sale', 
            'PRDBrand', 'category', 'like', 'avr_review', 'count_review', 
            'images', 'product_variation'
        ]
