from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # No extra blank rows
    readonly_fields = ('product', 'quantity', 'is_active', 'sub_total')  # Makes these fields read-only
    can_delete = False  # Prevent deletion from inline

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added', 'total_items')  # Fields to display in the list view
    search_fields = ('cart_id',)
    readonly_fields = ('date_added',)  # Makes date_added read-only
    inlines = [CartItemInline]

    def total_items(self, obj):
        return CartItem.objects.filter(cart=obj).count()
    total_items.short_description = 'Total Items'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active', 'sub_total')  # Fields to display in list view
    search_fields = ('product__name',)  # Add search capability
    list_filter = ('is_active', 'cart')  # Filters
    readonly_fields = ('sub_total',)  # Makes sub_total read-only

# Registering the models with custom admin
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
