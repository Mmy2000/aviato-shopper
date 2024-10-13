from django.contrib import admin
from .models import Category, Subcategory

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    show_change_link = True  # Adds a link to edit the subcategory
    fields = ('name', 'description')  # Fields to show in the inline form

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'subcategory_count')  # Display category name, description, and number of subcategories
    search_fields = ('name',)  # Adds search functionality for category names
    list_filter = ('name',)  # Adds filtering options for categories by name
    inlines = [SubcategoryInline]  # Allows subcategories to be managed inline
    ordering = ['name']  # Orders categories by name in the admin list view

    # Custom method to display subcategory count
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategory Count'  # Sets the column name in the list view

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')  # Display subcategory name, category, and description
    search_fields = ('name', 'category__name')  # Allows searching by subcategory and category name
    list_filter = ('category',)  # Adds a filter for categories
    ordering = ['name']  # Orders subcategories by name in the admin list view

admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
