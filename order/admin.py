from django.contrib import admin
from .models import Payment, Order, OrderProduct

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'payment_method', 'payment_paid', 'status', 'created_at', 'user')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'payment_method', 'user__username')
    readonly_fields = ('payment_id', 'payment_method', 'payment_paid', 'status', 'created_at', 'user')

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'email', 'order_total', 'status', 'created_at','payment_method', 'is_orderd')
    list_filter = ('status', 'created_at', 'is_orderd')
    search_fields = ('order_number', 'first_name', 'last_name', 'email','payment_method')
    fieldsets = (
        (None, {
            'fields': ('order_number', 'first_name', 'last_name', 'email', 'phone', 'address_line_1', 'address_line_2')
        }),
        ('Shipping Information', {
            'fields': ('zip_code', 'country', 'state', 'city', 'order_note', 'ip','payment_method'),
            'classes': ('collapse',),
        }),
        ('Order Summary', {
            'fields': ('order_total', 'tax', 'status', 'is_orderd'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def full_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    full_name.admin_order_field = 'first_name'  # Allows column ordering by this field

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'product_price', 'ordered', 'created_at', 'updated_at')
    list_filter = ('ordered', 'created_at')
    search_fields = ('product__name', 'order__order_number')
    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'variations', 'quantity', 'product_price', 'ordered'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
