from decimal import Decimal
from django.shortcuts import render , redirect

from order.models import Order, OrderProduct, Payment
from .forms import OrderForm
from cart.models import CartItem, Tax
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import datetime
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.


def paypal_payment(request):
    return render(request , 'payment.html')


def place_order(request,total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('product_list')
    grand_total = 0
    tax_obj = Tax.objects.last()
    tax_percentage = tax_obj.tax if tax_obj else Decimal('0.00')
    for cart_item in cart_items:
        total+=(cart_item.product.price * cart_item.quantity)
        quantity+=cart_item.quantity
    # Calculate the tax based on the total
    tax_amount = (tax_percentage * total) / Decimal('100')  # Calculate tax
    grand_total = total + tax_amount  # Grand total is the sum of the total and tax
    # Round the values to 2 decimal places
    total = round(total, 2)
    tax_amount = round(tax_amount, 2)
    grand_total = round(grand_total, 2)

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.payment_method = form.cleaned_data['payment_method']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax_amount
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_orderd=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax_amount,
                'grand_total': grand_total,
            }
            if data.payment_method == "cash":
                return redirect('cash_order')
            return render(request, 'payment.html', context)
        else:
            messages.error(request, 'Pls, Add your Delivery info!')
            return redirect('checkout')
        



def cash_order(request):
    current_user = request.user

    # Get the order that was just created
    order = Order.objects.filter(user=current_user, is_orderd=False).last()

    if not order:
        messages.error(request, "No order found.")
        return redirect('product_list')

    # Create a payment object for cash payment
    payment = Payment(
        user=current_user,
        payment_id=f"cash_{order.order_number}",  # Generate a payment id for cash payment
        payment_method="cash",
        payment_paid="False",  # Cash payment is considered as paid
        status="On Delivery",  # Set status to Paid
    )
    payment.save()

    # Update the order with the payment information
    order.payment = payment
    order.is_orderd = True
    order.status = "On Delivery"
    order.save()

    # Move all cart items to OrderProduct table and reduce stock
    cart_items = CartItem.objects.filter(user=current_user)

    for item in cart_items:
        # Create OrderProduct instance for each item in the cart
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

        # If there are variations, associate them with the order product
        order_product.variations.set(item.variations.all())
        order_product.save()

        # Reduce the stock of the product
        product = item.product
        product.stock -= item.quantity
        product.save()

    # Clear the user's cart after the order is placed
    cart_items.delete()

    # Send order received email to customer
    try:
        mail_subject = 'Thank you for your order!'
        message = render_to_string('order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
    except Exception as e:
        # Log the exception (optional)
        print(f"Failed to send email: {e}")

    # Provide a success message and redirect to a success page
    messages.success(request, "Thank you! Your order has been successfully placed.")
    return redirect('order_success')


def order_success(request):
    current_user = request.user

    # Get the last order placed by the user
    order = Order.objects.filter(user=current_user, is_orderd=True).last()
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    subtotal = 0
    for i in ordered_products:
        subtotal += i.product_price * i.quantity

    context = {
        'order': order,
        'subtotal': subtotal,
        'ordered_products': ordered_products,
    }
    return render(request , 'order_complete.html' , context)