from django.urls import path,include
from . import views

from rest_framework.routers import DefaultRouter
from .api_view import ProductViewSet, ProductImageViewSet, VariationViewSet

router = DefaultRouter()
router.register('api/products', ProductViewSet, basename='product_api')
router.register('api/product-images', ProductImageViewSet, basename='productimage_api')
router.register('api/variations', VariationViewSet, basename='variation_api')

urlpatterns = [
    path('' , views.product_list , name='product_list'),
    path('<str:product_id>' , views.product_details , name='product_details'),
    path('subcategory/<str:subcategory_id>/' , views.product_list , name='products_by_subcategory'),
    path('category/<str:category_id>/' , views.product_list , name='products_by_category'),
    path('brand/<str:brand_id>/' , views.product_list , name='products_by_brand'),
    path('search/' , views.search , name='search'),
    path('submit_review/<str:product_id>/',views.submit_review ,name='submit_review'),

    # API
    path('', include(router.urls)),
]
