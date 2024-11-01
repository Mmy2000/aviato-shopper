from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product , Variation
from .models import Cart , CartItem, Tax
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from .cart_utils import _cart_id
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
# Create your views here.


def add_to_cart(request , product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # if user is_authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product = product , variation_category__iexact = key , variation_value__iexact = value)
                    product_variation.append(variation)
                except:
                    pass
        
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save()


        is_cart_item_exists = CartItem.objects.filter(product=product , user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product , user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item = CartItem.objects.get(product=product , id=item_id)
                if "product-quantity" in request.POST and request.POST["product-quantity"].isdigit():
                    item.quantity += int(request.POST["product-quantity"])
                else:
                    item.quantity += 1
                item.save()
                messages.success(request,f"{product.name} updated successfully")
                
            else:
                item = CartItem.objects.create(product = product , user=current_user , quantity = request.POST['product-quantity'])
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                messages.success(request,"Product added successfully")
        else :
            cart_item = CartItem.objects.create(product = product , user=current_user , quantity = request.POST.get('product-quantity', 1))
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            messages.success(request,"Product added successfully")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    # if user is't_authenticated
    else:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product = product , variation_category__iexact = key , variation_value__iexact = value)
                    product_variation.append(variation)
                except:
                    pass
        
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save()


        is_cart_item_exists = CartItem.objects.filter(product=product , cart = cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product , cart = cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item = CartItem.objects.get(product=product , id=item_id)
                if "product-quantity" in request.POST and request.POST["product-quantity"].isdigit():
                    item.quantity += int(request.POST["product-quantity"])
                else:
                    item.quantity += 1
                item.save()
                messages.success(request,f"{product.name} updated successfully")
                
            else:
                item = CartItem.objects.create(product = product , cart = cart , quantity = request.POST['product-quantity'])
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                messages.success(request,"Product added successfully")
        else :
            cart_item = CartItem.objects.create(product = product , cart = cart , quantity = request.POST.get('product-quantity', 1))
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            messages.success(request,"Product added successfully")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def decrement_cart(request , product_id ,cart_item_id):
    
    product = get_object_or_404(Product , id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product , user = request.user , id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product , cart = cart ,id=cart_item_id )
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request,f'{product.name} updated Successfully')
        else:
            cart_item.delete()
            messages.success(request,f"{product.name} deleted successfully")
            
    except:
        pass
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_items=None):
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

    return render(request, 'cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
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
    
    return render(request , 'checkout.html' , context)