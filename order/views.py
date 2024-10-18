from decimal import Decimal
from django.shortcuts import render , redirect

from order.models import Order
from .forms import OrderForm
from cart.models import CartItem, Tax
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import datetime
import json
# Create your views here.

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
            return render(request, 'payment.html', context)
        else:
            messages.error(request, 'Pls, Add your Delivery info!')
            return redirect('checkout')