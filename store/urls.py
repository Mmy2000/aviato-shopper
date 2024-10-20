from django.urls import path,include
from . import views
from .api_view import ProductListApi,ProductCreateUpdateView,ProductDeleteView,ProductDetailApi


urlpatterns = [
    path('' , views.product_list , name='product_list'),
    path('<str:product_id>' , views.product_details , name='product_details'),
    path('subcategory/<str:subcategory_id>/' , views.product_list , name='products_by_subcategory'),
    path('category/<str:category_id>/' , views.product_list , name='products_by_category'),
    path('brand/<str:brand_id>/' , views.product_list , name='products_by_brand'),
    path('search/' , views.search , name='search'),
    path('submit_review/<str:product_id>/',views.submit_review ,name='submit_review'),

    # API
    path("api/products/", ProductListApi.as_view(), name="product_list"),
    path("api/product/<uuid:pk>/", ProductDetailApi.as_view(), name="product_details"),
    path('api/product/create/', ProductCreateUpdateView.as_view(), name='product-create'),  # POST for create
    path('api/product/update/<uuid:pk>/', ProductCreateUpdateView.as_view(), name='product-update'),  # PUT for update
    path('api/product/delete/<uuid:pk>/', ProductDeleteView.as_view(), name='product-delete'),  # DELETE for delete
]
