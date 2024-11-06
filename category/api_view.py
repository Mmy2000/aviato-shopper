from rest_framework import viewsets
from .models import Category
from .serializers import CategorySerializerFilter

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.prefetch_related('subcategories').all()
    serializer_class = CategorySerializerFilter