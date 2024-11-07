from django.contrib import admin
from .models import Product, ProductImage, Brand, Variation, ReviewRating
from django.utils.html import mark_safe

# Inline class for Product images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty image forms displayed initially

# Inline class for Variations
class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1  # Number of empty variation forms displayed initially
    list_display = ('variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)

# Admin class for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'PRDBrand', 'category', 'price', 'stock', 'on_sale', 'views', 'is_available', 'average_rating', 'review_count', 'created_at')
    search_fields = ('name', 'PRDBrand__name', 'category__name', 'description')
    list_filter = ('is_available', 'on_sale', 'category', 'PRDBrand', 'created_at')
    readonly_fields = ('slug', 'created_at', 'modified_date', 'views')
    list_editable = ('price', 'stock', 'is_available', 'on_sale')
    ordering = ['-created_at']
    inlines = [ProductImageInline, VariationInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image', 'PRDBrand', 'category', 'price', 'stock', 'is_available', 'on_sale')
        }),
        ('Additional Information', {
            'classes': ('collapse',),
            'fields': ('views', 'created_at', 'modified_date')
        }),
    )

    # Display average rating and review count in admin list
    def average_rating(self, obj):
        return obj.avr_review()
    average_rating.short_description = 'Avg. Rating'
    
    def review_count(self, obj):
        return obj.count_review()
    review_count.short_description = 'Review Count'

# Admin class for Brand
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'website', 'created_at', 'updated_at', 'product_count_in_brand')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)
    ordering = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'logo', 'description', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # Custom method to count the number of products in the brand
    def product_count_in_brand(self, obj):
        return obj.product_brand.count()
    product_count_in_brand.short_description = 'Product Count in Brand'

# Admin class for ProductImage
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_thumbnail')
    search_fields = ('product__name',)
    readonly_fields = ('product',)

    # Custom method to display a thumbnail of the image
    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return "No Image"

    image_thumbnail.short_description = 'Image Preview'  # Title for the column

# Admin class for Variation
@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('variation_category', 'is_active')
    search_fields = ('product__name', 'variation_value')
    ordering = ['product', 'variation_category', 'variation_value']

@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'subject', 'rating', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'rating')
    search_fields = ('user__username', 'product__name', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('user', 'product', 'subject', 'review', 'rating', 'status')
        }),
        ('Additional Information', {
            'fields': ('ip', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    