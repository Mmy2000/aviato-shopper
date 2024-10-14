from .models import Category , Subcategory
from store.models import Brand

def nav_links(request):
    categories_nav = Category.objects.all()
    subcategories_nav = Subcategory.objects.all()
    brands_nav = Brand.objects.all()
    context = {
        'categories_nav':categories_nav,
        'brands_nav':brands_nav,
        'subcategories_nav':subcategories_nav,
    }
    return context