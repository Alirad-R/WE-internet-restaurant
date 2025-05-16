from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity', 'unit_price', 'subtotal')
        read_only_fields = ('id', 'unit_price', 'subtotal')

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model
    """
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_date', 'status', 'total_amount', 
                  'payment_status', 'shipping_address', 'phone_number', 
                  'notes', 'updated_at', 'items')
        read_only_fields = ('id', 'customer', 'order_date', 'total_amount', 'updated_at')

class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Order
    """
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ('id', 'shipping_address', 'phone_number', 'notes', 'items')
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # Use 0 as initial total because we'll calculate it when adding items
        order = Order.objects.create(
            customer=self.context['request'].user,
            total_amount=0,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                **item_data
            )
        
        # Recalculate total
        order.total_amount = order.calculate_total()
        order.save()
        
        # Clear customer's cart after successful order
        try:
            cart = self.context['request'].user.cart
            cart.items.all().delete()
        except Exception:
            pass
            
        return order

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal')
        read_only_fields = ('id', 'subtotal')

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model
    """
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'item_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at') 