from django.shortcuts import render

from store.models import Product

# Create your views here.

def home(request):

    products = Product.objects.all().order_by('-views')
    context = {
        'products':products
    }
    return render(request,'home.html',context)

def custom_404_view(request, exception=None):
    return render(request, '404.html', {}, status=404)