from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from cart.models import CartItem , Tax
from .serializers import OrderSerializer
from django.conf import settings
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def get_cart_items(self, user):
        return CartItem.objects.filter(user=user)

    def calculate_totals(self, cart_items):
        total = sum(item.product.price * item.quantity for item in cart_items)
        quantity = sum(item.quantity for item in cart_items)
        tax_obj = Tax.objects.last()
        tax_percentage = tax_obj.tax if tax_obj else Decimal('0.00')
        tax_amount = (tax_percentage * total) / Decimal('100')
        grand_total = total + tax_amount
        return round(total, 2), round(tax_amount, 2), round(grand_total, 2)

    def post(self, request):
        current_user = request.user
        cart_items = self.get_cart_items(current_user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total, tax_amount, grand_total = self.calculate_totals(cart_items)
        
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Save order data
            order = serializer.save(user=current_user, order_total=grand_total, tax=tax_amount)
            order.ip = request.META.get('REMOTE_ADDR')

            # Generate order number
            current_date = datetime.now().strftime("%Y%m%d")
            order_number = f"{current_date}{order.id}"
            order.order_number = order_number
            order.save()

            # Return the order data along with cart details
            response_data = {
                'order': OrderSerializer(order).data,
                'total': total,
                'tax': tax_amount,
                'grand_total': grand_total,
                'cart_items': [{"product_name": item.product.name, "quantity": item.quantity, "price": item.product.price} for item in cart_items],
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
