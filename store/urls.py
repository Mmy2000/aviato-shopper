from django.urls import path,include

from . import views
from .api_view import AllProductImagesView, ProductImageCreateView, ProductImageDeleteView, ProductImageListView, ProductImageUpdateView, ProductListApi,ProductCreateUpdateView,ProductDeleteView,ProductDetailApi,CategoryViewSet,SubCategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/categories', CategoryViewSet)
router.register(r'api/subcategories', SubCategoryViewSet)

urlpatterns = [
    path('' , views.product_list , name='product_list'),
    path('<str:product_id>' , views.product_details , name='product_details'),
    path('subcategory/<str:subcategory_id>/' , views.product_list , name='products_by_subcategory'),
    path('category/<str:category_id>/' , views.product_list , name='products_by_category'),
    path('brand/<str:brand_id>/' , views.product_list , name='products_by_brand'),
    path('search/' , views.search , name='search'),
    path('submit_review/<str:product_id>/',views.submit_review ,name='submit_review'),
    path('add_to_favourit/<str:id>',views.add_to_favourit ,name='add_to_favourit'),

    # API
    path("api/products/", ProductListApi.as_view(), name="product_list_api"),
    path("api/product/<uuid:pk>/", ProductDetailApi.as_view(), name="product_details_api"),
    path('api/product/create/', ProductCreateUpdateView.as_view(), name='product-create'),  # POST for create
    path('api/product/update/<uuid:pk>/', ProductCreateUpdateView.as_view(), name='product-update'),  # PUT for update
    path('api/product/delete/<uuid:pk>/', ProductDeleteView.as_view(), name='product-delete'),  # DELETE for delete

    path('api/product/images/all/', AllProductImagesView.as_view(), name='all-product-images'),
    path('api/product/<uuid:product_id>/create/', ProductImageCreateView.as_view(), name='product-image-create'),  # POST: Add image to product
    path('api/product/<uuid:product_id>/images/', ProductImageListView.as_view(), name='product-image-list'),  # GET: List images for a product
    path('api/product/update/<uuid:product_id>/images/<int:image_id>/', ProductImageUpdateView.as_view(), name='product-image-update'),  # PUT: Update product image
    path('api/product/delete/<uuid:product_id>/images/<int:image_id>/', ProductImageDeleteView.as_view(), name='product-image-delete'),  # DELETE: Delete an image by product_id and image_id

    path('', include(router.urls)),
]
