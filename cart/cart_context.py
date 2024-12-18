from decimal import Decimal
from django.shortcuts import redirect, render,get_object_or_404
from store.models import Product
from .models import Cart , CartItem, Tax
from django.core.exceptions import ObjectDoesNotExist
from .cart_utils import _cart_id
from django.contrib import messages
from django.http import HttpResponseRedirect

def cart_context(request, total=0, quantity=0, cart_items=None):
    try:
        tax_obj = Tax.objects.last()  # Fetch the last Tax object
        tax_percentage = tax_obj.tax if tax_obj else Decimal('0.00')  # Get the tax value or default to 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user , is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using a session ID or similar method
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # Get active items in the cart
        
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity  # Sum up the product prices
            quantity += cart_item.quantity
        
        # Calculate the tax based on the total
        tax_amount = (tax_percentage * total) / Decimal('100')  # Calculate tax
        grand_total = total + tax_amount  # Grand total is the sum of the total and tax

        # Round the values to 2 decimal places
        total = round(total, 2)
        tax_amount = round(tax_amount, 2)
        grand_total = round(grand_total, 2)

    except ObjectDoesNotExist:
        # Handle case where no cart or cart items exist
        cart_items = []
        total = Decimal('0.00')
        quantity = 0
        tax_amount = Decimal('0.00')
        grand_total = Decimal('0.00')

    # Pass the data to the template
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'tax': tax_amount,
    }

    return dict(context)

def delete_cart(request , product_id ,cart_item_id ):
    
    product = get_object_or_404(Product , id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product , user = request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product , cart = cart , id=cart_item_id)
    cart_item.delete()
    messages.success(request,f'{product.name} deleted Successfully')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))