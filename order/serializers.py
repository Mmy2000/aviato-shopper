from rest_framework import serializers
from .models import Order, Payment

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'payment_method', 'email',
                  'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'