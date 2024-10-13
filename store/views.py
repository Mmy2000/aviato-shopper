from django.shortcuts import render
from .models import Product , Brand
from category.models import Category , Subcategory
# Create your views here.

def product_list(request):

    products = Product.objects.all().filter(is_available=True)
    product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count
    }

    return render(request , 'products/product_list.html' , context)