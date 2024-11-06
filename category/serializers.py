from rest_framework import serializers
from .models import Category, Subcategory

class SubcategorySerializerFilter(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'description', 'image']

class CategorySerializerFilter(serializers.ModelSerializer):
    subcategories = SubcategorySerializerFilter(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'subcategories']