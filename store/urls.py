from django.urls import path
from . import views
urlpatterns = [
    path('' , views.product_list , name='product_list'),
    path('subcategory/<str:subcategory_id>/' , views.product_list , name='products_by_subcategory'),
    path('category/<str:category_id>/' , views.product_list , name='products_by_category'),
    path('brand/<str:brand_id>/' , views.product_list , name='products_by_brand'),
]
