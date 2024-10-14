from django.contrib import admin
from .models import Category, Subcategory
from store.models import Product

# Inline admin for managing subcategories within categories
class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    show_change_link = True  # Adds a link to edit the subcategory
    fields = ('name', 'description')  # Fields to show in the inline form

# Admin class for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'description', 'subcategory_count', 'product_count_in_category')  # Displays name, description, subcategory count, and product count
    search_fields = ('name',)  # Adds search functionality for category names
    list_filter = ('name',)  # Adds filtering options for categories by name
    inlines = [SubcategoryInline]  # Allows subcategories to be managed inline
    ordering = ['name']  # Orders categories by name in the admin list view

    # Custom method to display subcategory count
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategory Count'  # Sets the column name in the list view

    # Custom method to display product count for the category
    def product_count_in_category(self, obj):
        return Product.objects.filter(category__in=obj.subcategories.all()).count()
    product_count_in_category.short_description = 'Product Count'  # Sets the column name for product count

# Admin class for Subcategory
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'category', 'description', 'product_count_in_subcategory')  # Displays subcategory name, category, description, and product count
    search_fields = ('name', 'category__name')  # Allows searching by subcategory and category name
    list_filter = ('category',)  # Adds a filter for categories
    ordering = ['name']  # Orders subcategories by name in the admin list view

    # Custom method to display product count for the subcategory
    def product_count_in_subcategory(self, obj):
        return obj.product_subcategory.count()
    product_count_in_subcategory.short_description = 'Product Count'  # Sets the column name for product count

# Register the models and their admin classes
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
