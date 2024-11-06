from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_view import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('api/', include(router.urls)),
]