from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from products.models import Product
from .models import Order, OrderItem, Cart, CartItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    CartSerializer,
    CartItemSerializer
)

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own orders
        return Order.objects.filter(customer=self.request.user).order_by('-order_date')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
        
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order if it's still pending
        """
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {"detail": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing the user's shopping cart
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # User can only access their own cart
        return Cart.objects.filter(customer=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        Get the user's cart or create if it doesn't exist
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add an item to the cart
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                product = Product.objects.get(id=product_id)
                
                # Check if item already exists in cart
                try:
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    cart_item.quantity += quantity
                    cart_item.save()
                except CartItem.DoesNotExist:
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=quantity
                    )
                
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data)
                
            except Product.DoesNotExist:
                return Response(
                    {"detail": "Product not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """
        Remove an item from the cart
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        
        try:
            product_id = request.data.get('product_id')
            if not product_id:
                return Response(
                    {"detail": "Product ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Item not in cart."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """
        Update the quantity of an item in the cart
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {"detail": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if int(quantity) < 1:
            return Response(
                {"detail": "Quantity must be at least 1"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity = int(quantity)
            cart_item.save()
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Item not in cart."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Clear all items from the cart
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        cart.items.all().delete()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Create an order from the cart items
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        
        if not cart.items.exists():
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get order details from request
        shipping_address = request.data.get('shipping_address')
        phone_number = request.data.get('phone_number')
        notes = request.data.get('notes', '')
        
        if not shipping_address or not phone_number:
            return Response(
                {"detail": "Shipping address and phone number are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                customer=request.user,
                shipping_address=shipping_address,
                phone_number=phone_number,
                notes=notes,
                total_amount=0  # Will be calculated after adding items
            )
            
            # Add items to order
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price
                )
                
            # Calculate total
            order.total_amount = order.calculate_total()
            order.save()
            
            # Clear cart
            cart.items.all().delete()
            
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 