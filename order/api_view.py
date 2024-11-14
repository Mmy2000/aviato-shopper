from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order,OrderProduct,Payment
from cart.models import CartItem , Tax
from .serializers import OrderSerializer
from django.conf import settings
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer, PaymentSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

# Initialize a logger
logger = logging.getLogger(__name__)


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def get_cart_items(self, user):
        return CartItem.objects.filter(user=user)

    def calculate_totals(self, cart_items):
        total = sum(item.product.price * item.quantity for item in cart_items)
        quantity = sum(item.quantity for item in cart_items)
        tax_obj = Tax.objects.last()
        tax_percentage = tax_obj.tax if tax_obj else Decimal('0.00')
        tax_amount = (tax_percentage * total) / Decimal('100')
        grand_total = total + tax_amount
        return round(total, 2), round(tax_amount, 2), round(grand_total, 2)

    def post(self, request):
        current_user = request.user
        cart_items = self.get_cart_items(current_user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total, tax_amount, grand_total = self.calculate_totals(cart_items)
        
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Save order data
            order = serializer.save(user=current_user, order_total=grand_total, tax=tax_amount)
            order.ip = request.META.get('REMOTE_ADDR')

            # Generate order number
            current_date = datetime.now().strftime("%Y%m%d")
            order_number = f"{current_date}{order.id}"
            order.order_number = order_number
            order.save()

            # Return the order data along with cart details
            response_data = {
                'order': OrderSerializer(order).data,
                'total': total,
                'tax': tax_amount,
                'grand_total': grand_total,
                'cart_items': [{"product_name": item.product.name, "quantity": item.quantity, "price": item.product.price} for item in cart_items],
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CashOrderView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         current_user = request.user

#         # Get the order that was just created
#         order = Order.objects.filter(user=current_user, is_orderd=False).last()

#         if not order:
#             return Response({"error": "No order found."}, status=status.HTTP_400_BAD_REQUEST)

#         # Create a payment object for cash payment
#         payment = Payment(
#             user=current_user,
#             payment_id=f"cash_{order.order_number}",
#             payment_method="cash",
#             payment_paid=False,  # Cash payment is considered as paid
#             status="On Delivery",  # Set status to On Delivery
#         )
#         payment.save()

#         # Update the order with the payment information
#         order.payment = payment
#         order.is_orderd = True
#         order.status = "On Delivery"
#         order.save()

#         # Move all cart items to OrderProduct table and reduce stock
#         cart_items = CartItem.objects.filter(user=current_user)

#         for item in cart_items:
#             order_product = OrderProduct(
#                 order=order,
#                 payment=payment,
#                 user=current_user,
#                 product=item.product,
#                 quantity=item.quantity,
#                 product_price=item.product.price,
#                 ordered=True
#             )
#             order_product.save()
#             order_product.variations.set(item.variations.all())
#             order_product.save()

#             # Reduce the stock of the product
#             product = item.product
#             product.stock -= item.quantity
#             product.save()

#         # Clear the user's cart after the order is placed
#         cart_items.delete()

#         # Send order received email to customer
#         # try:
#         #     mail_subject = 'Thank you for your order!'
#         #     message = render_to_string('order_recieved_email.html', {
#         #         'user': request.user,
#         #         'order': order,
#         #     })
#         #     send_mail(mail_subject, message, 'from@example.com', [request.user.email])
#         # except Exception as e:
#         #     return Response({"error": f"Failed to send email: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({
#             "message": "Thank you! Your order has been successfully placed.",
#             "order": OrderSerializer(order).data,
#             "payment": PaymentSerializer(payment).data
#         }, status=status.HTTP_201_CREATED)

class CashOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            current_user = request.user
            # Attempt to get the latest order for the user that hasn't been ordered
            order = Order.objects.filter(user=current_user, is_orderd=False).last()
            
            if not order:
                logger.error("No order found for user %s", current_user)
                return Response({"error": "No order found."}, status=status.HTTP_400_BAD_REQUEST)

            # Create a payment object for cash payment
            try:
                payment = Payment(
                    user=current_user,
                    payment_id=f"cash_{order.order_number}",
                    payment_method="cash",
                    payment_paid=False,  # Cash payment is considered as unpaid
                    status="On Delivery",  # Set status to On Delivery
                )
                payment.save()
            except Exception as e:
                logger.error("Failed to create payment: %s", e)
                return Response({"error": "Failed to create payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Update the order with the payment information
            try:
                order.payment = payment
                order.is_orderd = True
                order.status = "On Delivery"
                order.save()
            except Exception as e:
                logger.error("Failed to update order with payment information: %s", e)
                return Response({"error": "Failed to update order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Move all cart items to OrderProduct table and reduce stock
            try:
                cart_items = CartItem.objects.filter(user=current_user)
                if not cart_items.exists():
                    logger.warning("No cart items found for user %s", current_user)

                for item in cart_items:
                    order_product = OrderProduct(
                        order=order,
                        payment=payment,
                        user=current_user,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True
                    )
                    order_product.save()
                    order_product.variations.set(item.variations.all())
                    order_product.save()

                    # Reduce the stock of the product
                    product = item.product
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                        product.save()
                    else:
                        logger.error("Insufficient stock for product %s", product)
                        return Response({"error": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)

                # Clear the user's cart after the order is placed
                cart_items.delete()
            except Exception as e:
                logger.error("Failed to process cart items and update stock: %s", e)
                return Response({"error": "Failed to process cart items."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Optional: Send order received email to customer
            # try:
            #     mail_subject = 'Thank you for your order!'
            #     message = render_to_string('order_recieved_email.html', {
            #         'user': request.user,
            #         'order': order,
            #     })
            #     send_mail(mail_subject, message, 'from@example.com', [request.user.email])
            # except Exception as e:
            #     logger.error("Failed to send email: %s", e)
            #     return Response({"error": f"Failed to send email: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "message": "Thank you! Your order has been successfully placed.",
                "order": OrderSerializer(order).data,
                "payment": PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # General error handling
            logger.error("An unexpected error occurred: %s", e)
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)