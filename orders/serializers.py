from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem, OrderStatusHistory, ReturnItem, ReturnRequest
from products.serializers import ProductSerializer
from accounts.serializers import UserSerializer
from coupons.serializers import CouponSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model
    """
    product_details = ProductSerializer(source='product', read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='get_total')

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_details', 'quantity', 'unit_price', 'notes', 'total')
        read_only_fields = ('unit_price',)

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This product is no longer available")
        return value

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model - used for list and retrieve operations
    """
    items = OrderItemSerializer(many=True, read_only=True)
    customer_details = UserSerializer(source='customer', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    coupon = CouponSerializer(read_only=True)
    total_after_discount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    can_cancel = serializers.BooleanField(read_only=True)
    can_refund = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'customer', 'customer_details', 'status', 'status_display',
            'payment_status', 'payment_status_display', 'delivery_method', 'delivery_method_display',
            'created_at', 'updated_at', 'confirmed_at', 'estimated_delivery', 'delivered_at',
            'subtotal', 'tax', 'delivery_fee', 'total', 'delivery_address', 'delivery_notes',
            'special_instructions', 'cancellation_reason', 'refund_reason', 'items',
            'coupon', 'discount_amount', 'total_after_discount',
            'can_cancel', 'can_refund'
        )
        read_only_fields = (
            'order_number', 'customer', 'created_at', 'updated_at', 'confirmed_at',
            'delivered_at', 'subtotal', 'tax', 'total', 'discount_amount', 'total_after_discount'
        )

class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new orders
    """
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'delivery_method', 'delivery_address', 'delivery_notes',
            'special_instructions', 'items'
        )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Generate unique order number (you might want to use a more sophisticated method)
        import uuid
        order_number = str(uuid.uuid4().hex[:10].upper())
        
        # Create order
        order = Order.objects.create(
            customer=self.context['request'].user,
            order_number=order_number,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            product = item_data['product']
            OrderItem.objects.create(
                order=order,
                unit_price=product.price,  # Use current product price
                **item_data
            )
        
        # Calculate totals
        order.calculate_total()
        order.save()
        
        return order

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for OrderStatusHistory model
    """
    changed_by = UserSerializer(read_only=True)
    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ('id', 'old_status', 'old_status_display', 'new_status', 
                 'new_status_display', 'changed_by', 'changed_at', 'notes')
        read_only_fields = fields

class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating orders with status change validation
    """
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    valid_status_transitions = serializers.ListField(child=serializers.CharField(), read_only=True)
    status_message = serializers.CharField(read_only=True)
    status_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = (
            'status', 'payment_status', 'delivery_method', 'estimated_delivery',
            'delivery_address', 'delivery_notes', 'special_instructions',
            'cancellation_reason', 'refund_reason', 'status_history',
            'valid_status_transitions', 'status_message', 'status_notes'
        )

    def validate_status(self, value):
        instance = self.instance
        if not instance:
            raise serializers.ValidationError("Cannot update status without an existing order.")
            
        if not instance.can_transition_to(value):
            valid_transitions = instance.get_valid_status_transitions()
            raise serializers.ValidationError(
                f"Invalid status transition. Current: {instance.status}. "
                f"Valid transitions: {', '.join(valid_transitions)}"
            )
        return value

    def update(self, instance, validated_data):
        status_notes = validated_data.pop('status_notes', None)
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        # If status is changing, use the change_status method
        if new_status != old_status:
            try:
                instance.change_status(
                    new_status,
                    user=self.context['request'].user,
                    notes=status_notes
                )
            except ValueError as e:
                raise serializers.ValidationError(str(e))

        # Update other fields
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Add dynamic fields to the response
        """
        data = super().to_representation(instance)
        data['valid_status_transitions'] = instance.get_valid_status_transitions()
        data['status_message'] = instance.get_status_message()
        return data

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

class ReturnItemSerializer(serializers.ModelSerializer):
    """
    Serializer for ReturnItem model
    """
    product_details = serializers.SerializerMethodField()
    original_quantity = serializers.IntegerField(source='order_item.quantity', read_only=True)

    class Meta:
        model = ReturnItem
        fields = ('id', 'order_item', 'quantity', 'reason', 'description',
                 'condition_images', 'product_details', 'original_quantity')
        read_only_fields = ('product_details', 'original_quantity')

    def get_product_details(self, obj):
        return {
            'name': obj.order_item.product.name,
            'price': obj.order_item.unit_price,
            'image': obj.order_item.product.image.url if obj.order_item.product.image else None
        }

    def validate_quantity(self, value):
        order_item = self.initial_data.get('order_item')
        if order_item and value > order_item.quantity:
            raise serializers.ValidationError(
                "Return quantity cannot exceed original order quantity"
            )
        return value

class ReturnRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for ReturnRequest model - used for list and retrieve
    """
    items = ReturnItemSerializer(many=True, read_only=True)
    customer_details = UserSerializer(source='customer', read_only=True)
    order_details = OrderSerializer(source='order', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    return_type_display = serializers.CharField(source='get_return_type_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    reviewed_by_details = UserSerializer(source='reviewed_by', read_only=True)

    class Meta:
        model = ReturnRequest
        fields = (
            'id', 'order', 'order_details', 'customer', 'customer_details',
            'return_type', 'return_type_display', 'reason', 'reason_display',
            'status', 'status_display', 'description', 'proof_images',
            'created_at', 'updated_at', 'reviewed_at', 'reviewed_by',
            'reviewed_by_details', 'admin_notes', 'rejection_reason',
            'refund_amount', 'items'
        )
        read_only_fields = (
            'status', 'reviewed_at', 'reviewed_by', 'admin_notes',
            'rejection_reason', 'refund_amount'
        )

class ReturnRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new return requests
    """
    items = ReturnItemSerializer(many=True)

    class Meta:
        model = ReturnRequest
        fields = (
            'order', 'return_type', 'reason', 'description',
            'proof_images', 'items'
        )

    def validate_order(self, value):
        # Check if order belongs to the user
        if value.customer != self.context['request'].user:
            raise serializers.ValidationError("You can only return your own orders")
        
        # Check if order is delivered
        if value.status != 'delivered':
            raise serializers.ValidationError("You can only return delivered orders")
        
        # Check if order already has a pending return request
        if value.return_requests.filter(status='pending').exists():
            raise serializers.ValidationError("This order already has a pending return request")
        
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Create return request
        return_request = ReturnRequest.objects.create(
            customer=self.context['request'].user,
            **validated_data
        )
        
        # Create return items
        for item_data in items_data:
            ReturnItem.objects.create(
                return_request=return_request,
                **item_data
            )
        
        return return_request

class ReturnRequestReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reviewing return requests
    """
    class Meta:
        model = ReturnRequest
        fields = ('status', 'refund_amount', 'admin_notes', 'rejection_reason')
        read_only_fields = ('status',)

    def validate(self, data):
        instance = self.instance
        if not instance.can_review():
            raise serializers.ValidationError(
                "This return request cannot be reviewed"
            )
        return data 