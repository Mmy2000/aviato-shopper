from django.shortcuts import render
from .models import Product
# Create your views here.

def product_list(request):

    products = Product.objects.all().filter(is_available=True)
    context = {
        'products':products
    }

    return render(request , 'products/product_list.html' , context)