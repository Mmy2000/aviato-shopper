
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from settings.views import  custom_404_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('settings.urls') ),
    path('products/' , include('store.urls')),
    path('accounts/' , include('accounts.urls')),
    path('cart/' , include('cart.urls')),
    path('order/' , include('order.urls')),
    path('categories/' , include('category.urls')),
]
urlpatterns +=  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

