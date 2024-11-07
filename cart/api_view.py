from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CartItem, Cart
from store.models import Product, Variation
from .serializers import CartItemSerializer, CartSerializer
from django.shortcuts import get_object_or_404

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user, is_active=True)

    def get_full_cart_response(self, cart):
        """Helper method to return the full cart details."""
        serializer = CartSerializer(cart)
        return serializer.data

    def create(self, request, *args, **kwargs):
        data = request.data
        product = get_object_or_404(Product, id=data['product_id'])
        cart, _ = Cart.objects.get_or_create(cart_id=request.session.session_key)

        # Retrieve variations if provided
        variation_ids = data.get('variations', [])
        if variation_ids:
            variations = Variation.objects.filter(id__in=variation_ids)
        else:
            variations = []

        # Check for an existing cart item with the same product and variations
        existing_cart_items = CartItem.objects.filter(user=request.user, product=product, cart=cart)
        for cart_item in existing_cart_items:
            if set(cart_item.variations.all()) == set(variations):
                # Same product and variations found, update quantity only
                cart_item.quantity += int(data.get('quantity', 1))
                cart_item.save()
                return Response(self.get_full_cart_response(cart), status=status.HTTP_200_OK)

        # No matching cart item with the same variations, create a new one
        cart_item = CartItem.objects.create(
            user=request.user,
            product=product,
            cart=cart,
            quantity=data.get('quantity', 1)
        )
        if variations:
            cart_item.variations.set(variations)

        return Response(self.get_full_cart_response(cart), status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        cart = instance.cart

        # Update quantity if provided
        instance.quantity = request.data.get("quantity", instance.quantity)

        # Handle variations only if provided
        variation_ids = request.data.get('variations', [])
        if variation_ids:
            variations = Variation.objects.filter(id__in=variation_ids)
            instance.variations.set(variations)
        
        instance.save()
        return Response(self.get_full_cart_response(cart), status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve the full cart details."""
        cart = get_object_or_404(Cart, cart_id=request.session.session_key)
        return Response(self.get_full_cart_response(cart), status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Delete a cart item and return the updated cart details."""
        instance = self.get_object()
        cart = instance.cart
        instance.delete()
        return Response(self.get_full_cart_response(cart), status=status.HTTP_200_OK)