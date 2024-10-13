from django.contrib import admin
from .models import Product, ProductImage, Brand

# Inline class for Product images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty image forms displayed initially
    readonly_fields = ('image',)

# Admin class for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'PRDBrand', 'category', 'price', 'stock', 'views', 'is_available', 'created_at')
    search_fields = ('name', 'PRDBrand__name', 'category__name', 'description')
    list_filter = ('is_available', 'category', 'PRDBrand', 'created_at')
    readonly_fields = ('slug', 'created_at', 'modified_date', 'views')
    list_editable = ('price', 'stock', 'is_available')
    ordering = ['-created_at']
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image', 'PRDBrand', 'category', 'price', 'stock', 'is_available')
        }),
        ('Additional Information', {
            'classes': ('collapse',),
            'fields': ('views', 'created_at', 'modified_date')
        }),
    )

# Admin class for Brand
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at', 'updated_at')
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

# Admin class for ProductImage
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__name',)
    readonly_fields = ('product',)
