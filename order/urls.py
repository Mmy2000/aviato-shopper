from django.urls import path
from . import views
from .api_view import  CreatePayPalPaymentView, ExecutePayPalPaymentView, PlaceOrderView,CashOrderView
urlpatterns = [
    path('place_order/' , views.place_order , name='place_order' ),
    path('cash-order/', views.cash_order, name='cash_order'),
    path('paypal_payment/', views.paypal_payment, name='paypal_payment'),
    path('stripe_payment/', views.stripe_payment , name='stripe_payment'),
    path('order-success/', views.order_success, name='order_success'), 
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),

    # API

    path('place_order_api/', PlaceOrderView.as_view(), name='place_order_api'),
    path('cash-order_api/', CashOrderView.as_view(), name='cash_order_api'),
    path('create-paypal-payment/', CreatePayPalPaymentView.as_view(), name='create-paypal-payment'),
    path('execute-paypal-payment/', ExecutePayPalPaymentView.as_view(), name='execute-paypal-payment'),
]
