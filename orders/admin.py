from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'total_amount', 'payment_status')
    list_filter = ('status', 'payment_status', 'order_date')
    search_fields = ('customer__username', 'customer__email', 'shipping_address')
    readonly_fields = ('order_date', 'total_amount')
    inlines = [OrderItemInline]
    list_per_page = 20

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'item_count', 'total', 'updated_at')
    search_fields = ('customer__username', 'customer__email')
    readonly_fields = ('created_at', 'updated_at', 'total', 'item_count')
    inlines = [CartItemInline] 