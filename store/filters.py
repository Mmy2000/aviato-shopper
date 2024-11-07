import django_filters
from django_filters import rest_framework as filters
from rest_framework import generics
from .models import Product, Variation

class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__category__id", lookup_expr='iexact')
    subcategory = filters.CharFilter(field_name="category__id", lookup_expr='iexact')
    brand = filters.CharFilter(field_name="PRDBrand__id", lookup_expr='iexact')
    variation = filters.CharFilter(method='filter_variation')
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'brand', 'min_price', 'max_price']

    def filter_variation(self, queryset, name, value):
        return queryset.filter(product_variation__variation_value__iexact=value)

