from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem

# Remove OrderItemInline and CartItemInline because their models lack ForeignKeys

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'status', 'total', 'payment_status')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number',)
    readonly_fields = ('created_at', 'total')
    list_per_page = 20

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_count', 'total', 'updated_at')
    search_fields = ('id',)
    readonly_fields = ('created_at', 'updated_at', 'total', 'item_count') 