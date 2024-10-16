from django.urls import path
from . import views
from .cart_context import delete_cart
urlpatterns = [
    path('' , views.cart , name='cart'),
    path('add_to_cart/<str:product_id>/' , views.add_to_cart , name='add_to_cart'),
    path('decrement_cart/<str:product_id>/<str:cart_item_id>/' , views.decrement_cart , name='decrement_cart'),
    path('delete_cart/<str:product_id>/<str:cart_item_id>/' , delete_cart , name='delete_cart'),
]
