import random
import string
from rest_framework import serializers

from order.models import Order, OrderProduct, Payment
from store.models import Product, Variation
from store.serializers import VariationSerializer
from .models import User , Profile
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','first_name','last_name','username','full_name','phone_number','is_admin','is_staff','is_active','is_superadmin']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def generate_username(self, first_name, last_name):
        # Use first name and last name to generate username and append a random string
        base_username = f"{first_name.lower()}{last_name.lower()}"
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return base_username + random_string

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        # Automatically generate username
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        username = self.generate_username(first_name, last_name)

        user = User.objects.create(username=username, **validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials, please try again.")
    

class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=True)
    last_name = serializers.CharField(source='user.last_name', required=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'user', 'first_name', 'last_name', 'image', 'about', 
            'country', 'address_line_1', 'address_line_2', 
            'headline', 'city','full_name','full_address'
        ]
        read_only_fields = ['user']  # Prevent direct editing of user field

    def update(self, instance, validated_data):
        # Handle updating the user's first and last name
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        # Update profile fields
        return super().update(instance, validated_data)
    


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image']  # Adjust fields as per your `Product` model

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_id', 'payment_method', 'payment_paid', 'status', 'created_at']
        
class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    variations = VariationSerializer(many=True)

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'variations', 'quantity', 'product_price', 'ordered']
        

class OrderSerializer(serializers.ModelSerializer):
    order_products = serializers.SerializerMethodField()
    payment_details = PaymentSerializer(source='payment', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'order_total', 'tax', 'created_at',
            'updated_at', 'is_orderd', 'full_name', 'full_address', 'order_products',
            'payment_details'
        ]

    def get_order_products(self, obj):
        order_products = OrderProduct.objects.filter(order=obj)
        return OrderProductSerializer(order_products, many=True).data