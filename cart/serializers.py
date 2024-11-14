from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem, Tax
from store.models import Product,Variation
from django.core.exceptions import ObjectDoesNotExist


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ['id', 'variation_category', 'variation_value']


from django.conf import settings
from rest_framework import serializers
from .models import CartItem, Variation
from .serializers import VariationSerializer

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['tax']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.CharField(source="product.price", read_only=True)
    product_image = serializers.SerializerMethodField()  # Change to SerializerMethodField
    variations = serializers.PrimaryKeyRelatedField(queryset=Variation.objects.all(), many=True, required=False)
    variation_details = VariationSerializer(source="variations", many=True, read_only=True)
    total = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'product_image', 'quantity', 
                  'variations', 'variation_details', 'sub_total', 'total','tax_amount', 'is_active']

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product.image and request:
            return request.build_absolute_uri(obj.product.image.url)
        return None

    def validate_variations(self, value):
        """Validate that the variations belong to the selected product."""
        product = self.initial_data.get('product')
        if product and value:
            for variation in value:
                if variation.product.id != product.id:
                    raise serializers.ValidationError("Variation does not belong to this product.")
        return value

    def get_total(self, obj):
        return obj.sub_total()
    
    def get_tax_amount(self, obj):
        total_price = self.get_total(obj)
        try:
            tax = Tax.objects.first()  # Assumes there's only one tax rate
            return tax.calculate_tax(total_price)
        except ObjectDoesNotExist:
            return Decimal('0.00')

    def create(self, validated_data):
        variations = validated_data.pop('variations', [])
        cart_item = CartItem.objects.create(**validated_data)
        cart_item.variations.set(variations)
        return cart_item

    def update(self, instance, validated_data):
        variations = validated_data.pop('variations', [])
        instance.quantity = validated_data.get('quantity', instance.quantity)
        if variations:
            instance.variations.set(variations)
        instance.save()
        return instance



class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_id', 'date_added', 'cart_items', 'total_price', 'tax_amount']

    def get_total_price(self, obj):
        # Calculate the sum of the total prices for all active cart items in the cart
        return sum(item.sub_total() for item in obj.cartitem_set.filter(is_active=True))

    def get_tax_amount(self, obj):
        total_price = self.get_total_price(obj)
        try:
            tax = Tax.objects.first()  # Assumes there's only one tax rate
            return tax.calculate_tax(total_price)
        except ObjectDoesNotExist:
            return Decimal('0.00')
