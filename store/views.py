from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponseRedirect
from order.models import OrderProduct
from store.forms import ReviewForm
from .models import Product , Brand , ProductImage, ReviewRating
from category.models import Category , Subcategory
from django.core.paginator import Paginator
from cart.models import CartItem
from cart.cart_utils import _cart_id
from django.db.models.query_utils import Q
from django.contrib import messages

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
        reviews = ReviewRating.objects.filter(product_id=single_product.id , status=True)
        if request.user.is_authenticated:
            in_cart = CartItem.objects.filter(user=request.user , product = product_id).exists()
            try:
                orderproduct = OrderProduct.objects.filter(user=request.user , product_id=single_product.id).exists()
            except OrderProduct.DoesNotExist:
                orderproduct = None
        else:
            orderproduct = None
            in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request) , product = product_id).exists()
    except Exception as e:
        raise e
    
    single_product.views+=1
    single_product.save()
    product_gallary = ProductImage.objects.filter(product_id=single_product.id)
    related = Product.objects.filter(category=single_product.category)
    orderproduct_counter =  OrderProduct.objects.filter( product_id=single_product.id)
    orderproduct_count = orderproduct_counter.count()
    
    context = {
        'single_product':single_product,
        'product_gallary':product_gallary,
        'related':related,
        'in_cart':in_cart,
        'reviews':reviews,
        'orderproduct':orderproduct,
        'orderproduct_count':orderproduct_count
    }

    return render(request , 'products/product_details.html' , context)

def search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q :
            product = Product.objects.order_by('-created_at').filter(
                Q(description__icontains=q ) |
                Q( name__icontains=q)
                )
            paginator = Paginator(product, 9)  # Show 9 products per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            product_count = product.count()
        else :
            return render(request , 'products/product_list.html')
    context = {
        'products':page_obj , 
        'product_count':product_count
    }
    return render(request , 'products/product_list.html', context)

def submit_review(request , product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method =="POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id , product__id=product_id)
            form = ReviewForm(request.POST , instance=reviews)
            form.save()
            messages.success(request,'Thank You , Your Review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,'Thank You , Your Review has been submitted.')
                return redirect(url)

def add_to_favourit(request,id):
    product = Product.objects.get(id=id)
    if request.user in product.like.all():
        product.like.remove(request.user.id)
        messages.success(request,'Product deleted Successfully from Favorite')
    else:
        product.like.add(request.user.id)
        messages.success(request,'Product added Successfully to Favorite')
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))