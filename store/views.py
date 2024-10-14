from django.shortcuts import get_object_or_404, render
from .models import Product , Brand
from category.models import Category , Subcategory
# Create your views here.

def product_list(request,subcategory_id=None,category_id=None):

    subcategories = None
    products = None
    categories = None

    if subcategory_id != None :
        subcategories = get_object_or_404(Subcategory,id = subcategory_id)
        products = Product.objects.filter(category=subcategories  ,is_available=True)
        product_count = products.count()
    elif category_id != None:
        categories = get_object_or_404(Category , id=category_id)
        products = Product.objects.filter(category__category=categories  ,is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count
    }

    return render(request , 'products/product_list.html' , context)