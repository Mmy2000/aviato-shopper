from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'payment_method', 'email',
                  'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']