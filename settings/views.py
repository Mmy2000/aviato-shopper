from django.shortcuts import render
from rest_framework.generics import ListAPIView
from store.models import Product
from store.serializers import ProductSerializer
# Create your views here.

def home(request):

    products = Product.objects.all().order_by('-views')
    context = {
        'products':products
    }
    return render(request,'home.html',context)

def custom_404_view(request, exception=None):
    return render(request, '404.html', {}, status=404)

class LastSixProductsView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.order_by('-id')[:6]