from rest_framework import serializers
from order.models import Order

class OrderSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField( read_only=True)
    full_address = serializers.CharField( read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number', 'full_name', 'phone', 'email', 
            'full_address', 'order_total', 'status', 'created_at',
        ]


