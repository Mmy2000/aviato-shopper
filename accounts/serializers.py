import random
import string
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


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