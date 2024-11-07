from django.urls import path,include

from . import views
from .cart_context import delete_cart
from rest_framework.routers import DefaultRouter
from .api_view import CartItemViewSet

router = DefaultRouter()
router.register(r'api/cart-items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('' , views.cart , name='cart'),
    path('add_to_cart/<str:product_id>/' , views.add_to_cart , name='add_to_cart'),
    path('decrement_cart/<str:product_id>/<str:cart_item_id>/' , views.decrement_cart , name='decrement_cart'),
    path('delete_cart/<str:product_id>/<str:cart_item_id>/' , delete_cart , name='delete_cart'),
    path('checkout/' , views.checkout , name='checkout'),

    # API
    path('', include(router.urls)),

]
