from rest_framework import serializers
from .models import Cart, CartItem, Tax
from store.models import Product,Variation

class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ['id', 'variation_category', 'variation_value']


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.CharField(source="product.price", read_only=True)
    variations = serializers.PrimaryKeyRelatedField(queryset=Variation.objects.all(), many=True, required=False)
    variation_details = VariationSerializer(source="variations", many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'product_name','product_price', 'quantity', 'variations', 'variation_details', 'sub_total', 'total', 'is_active']

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

    class Meta:
        model = Cart
        fields = ['id', 'cart_id', 'date_added', 'cart_items', 'total_price']

    def get_total_price(self, obj):
        # Calculate the sum of the total prices for all active cart items in the cart
        return sum(item.sub_total() for item in obj.cartitem_set.filter(is_active=True))
