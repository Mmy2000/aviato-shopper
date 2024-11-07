from django.contrib import admin
from .models import Cart, CartItem, Tax

# Inline for displaying CartItem in the Cart admin page
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # No extra blank rows
    readonly_fields = ('product', 'quantity', 'is_active', 'sub_total', 'variations')  # Fields to be read-only
    can_delete = False  # Prevent deletion of items from inline
    show_change_link = True  # Allows clicking to change the cart item

# Custom admin for Cart model
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','cart_id', 'date_added', 'total_items', 'cart_total')  # Show total items and cart total
    search_fields = ('cart_id',)
    readonly_fields = ('date_added', 'cart_total')  # Makes date_added and cart_total read-only
    inlines = [CartItemInline]
    
    def total_items(self, obj):
        """Calculate total items in the cart."""
        return CartItem.objects.filter(cart=obj).count()
    
    total_items.short_description = 'Total Items'
    
    def cart_total(self, obj):
        """Calculate the total price of the cart."""
        cart_items = CartItem.objects.filter(cart=obj)
        total = sum(item.sub_total() for item in cart_items)
        return f"${total:.2f}"  # Format the total as currency
    
    cart_total.short_description = 'Cart Total'

# Custom admin for CartItem model
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'cart', 'quantity', 'is_active', 'sub_total', 'variations_display')  # Display variations
    search_fields = ('product__name', 'cart__cart_id')  # Search by product name and cart ID
    list_filter = ('is_active', 'cart')  # Filters for is_active and cart
    readonly_fields = ('sub_total', 'variations_display')  # Make sub_total and variations read-only
    
    def variations_display(self, obj):
        """Display variations in a readable format."""
        return ", ".join([str(variation) for variation in obj.variations.all()])
    
    variations_display.short_description = 'Variations'

# Register the models with custom admin
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Tax)
