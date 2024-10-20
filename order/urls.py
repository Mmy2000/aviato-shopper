from django.urls import path
from . import views
urlpatterns = [
    path('place_order/' , views.place_order , name='place_order' ),
    path('cash-order/', views.cash_order, name='cash_order'),
    path('paypal_payment/', views.paypal_payment, name='paypal_payment'),
    path('stripe_payment/', views.stripe_payment , name='stripe_payment'),
    path('order-success/', views.order_success, name='order_success'), 
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
]
