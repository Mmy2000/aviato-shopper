from django.shortcuts import get_object_or_404, render
from .models import Product , Brand , ProductImage
from category.models import Category , Subcategory
from django.core.paginator import Paginator

# Create your views here.

def product_list(request,subcategory_id=None,category_id=None,brand_id=None):

    subcategories = None
    products = None
    categories = None
    brands = None

    if subcategory_id != None :
        subcategories = get_object_or_404(Subcategory,id = subcategory_id)
        products = Product.objects.filter(category=subcategories  ,is_available=True)
        product_count = products.count()
        paginator = Paginator(products, 9)  # Show 9 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    elif category_id != None:
        categories = get_object_or_404(Category , id=category_id)
        products = Product.objects.filter(category__category=categories  ,is_available=True)
        product_count = products.count()
        paginator = Paginator(products, 9)  # Show 9 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    elif brand_id != None:
        brands = get_object_or_404(Brand , id=brand_id)
        products = Product.objects.filter(PRDBrand=brands  ,is_available=True)
        product_count = products.count()
        paginator = Paginator(products, 9)  # Show 9 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()
        paginator = Paginator(products, 9)  # Show 9 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    context = {
        'products':page_obj,
        'product_count':product_count
    }

    return render(request , 'products/product_list.html' , context)

def product_details(request,product_id):

    try:
        single_product = Product.objects.get(id=product_id)
    except Exception as e:
        raise e
    
    single_product.views+=1
    single_product.save()
    product_gallary = ProductImage.objects.filter(product_id=single_product.id)
    related = Product.objects.filter(category=single_product.category)
    
    context = {
        'single_product':single_product,
        'product_gallary':product_gallary,
        'related':related,
    }

    return render(request , 'products/product_details.html' , context)