from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from products.models import Product
from .models import Order, OrderItem, Cart, CartItem, ReturnRequest, Wallet, Transaction
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderItemSerializer,
    OrderStatusHistorySerializer,
    ReturnRequestSerializer,
    ReturnRequestCreateSerializer,
    ReturnRequestReviewSerializer
)
from django.db import models
from .reports import SalesReportGenerator
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAdminUser

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.prefetch_related(
            'items', 
            'items__product',
            'status_history',
            'status_history__changed_by'
        )
        
        if user.is_staff:
            # Staff can see all orders
            pass
        else:
            # Regular users can only see their own orders
            queryset = queryset.filter(customer=user)
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        
        # Order by
        order_by = self.request.query_params.get('order_by', '-created_at')
        return queryset.order_by(order_by)
    
    #To pay
    @action(detail=True, methods=['post'], url_path='pay') #This lets us call POST /api/orders/12/pay/
    def pay(self, request, pk=None):
        order = self.get_object()
        try:
            order.pay()
            return Response({'detail': 'Order paid successfully'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    #To confirm payment
    @action(detail=True, methods=['post'], url_path='confirm_payment') #/api/orders/5/confirm-payment/
    def confirm_payment(self, request, pk=None):
        order = self.get_object()
        try:
            order.pay()
            return Response({'detail': 'Order paid successfully'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    #To reject payment
    @action(detail=True, methods=['post'], url_path='reject_payment') #/api/orders/5/reject-payment/
    def reject_payment(self, request, pk=None):
        order = self.get_object()
        if order.payment_status != 'pending':
            return Response({'error': 'only pending orders can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
        order.payment_status = 'rejected'
        order.save()
        return Response({'detail': 'Order rejected successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='sales_report')
    def sales_report(self, request):
        
        #optional filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day')
        
        queryset = Order.objects.filter(payment_status='paid')
        
        #apply date filters
        if start_date:
            queryset = queryset.filter(order_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__date__lte=end_date)
            
        #grouping
        if group_by == 'month':
            date_trunc = TruncMonth('order_date')
        elif group_by == 'year':
            date_trunc = TruncYear('order_date')
        else:
            date_trunc = TruncDate('order_date')
            
        report = (
            queryset
            .annotate(period=date_trunc)
            .values('period')
            .annotate(
                total=Sum('total_amount'),
                order_count=Count('id'),
            )
        )
        
        return Response(report)
        
    
    #To pay
    @action(detail=True, methods=['post'], url_path='pay') #This lets us call POST /api/orders/12/pay/
    def pay(self, request, pk=None):
        order = self.get_object()
        try:
            order.pay()
            return Response({'detail': 'Order paid successfully'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    #To confirm payment
    @action(detail=True, methods=['post'], url_path='confirm_payment') #/api/orders/5/confirm-payment/
    def confirm_payment(self, request, pk=None):
        order = self.get_object()
        try:
            order.pay()
            return Response({'detail': 'Order paid successfully'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    #To reject payment
    @action(detail=True, methods=['post'], url_path='reject_payment') #/api/orders/5/reject-payment/
    def reject_payment(self, request, pk=None):
        order = self.get_object()
        if order.payment_status != 'pending':
            return Response({'error': 'only pending orders can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
        order.payment_status = 'rejected'
        order.save()
        return Response({'detail': 'Order rejected successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='sales_report')
    def sales_report(self, request):
        
        #optional filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day')
        
        queryset = Order.objects.filter(payment_status='paid')
        
        #apply date filters
        if start_date:
            queryset = queryset.filter(order_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__date__lte=end_date)
            
        #grouping
        if group_by == 'month':
            date_trunc = TruncMonth('order_date')
        elif group_by == 'year':
            date_trunc = TruncYear('order_date')
        else:
            date_trunc = TruncDate('order_date')
            
        report = (
            queryset
            .annotate(period=date_trunc)
            .values('period')
            .annotate(
                total=Sum('total_amount'),
                order_count=Count('id'),
            )
        )
        
        return Response(report)
        
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        with transaction.atomic():
            order = serializer.save()
            # Additional actions after order creation (e.g., send notifications)
    
    def perform_update(self, serializer):
        with transaction.atomic():
            instance = serializer.instance
            old_status = instance.status
            order = serializer.save()
            
            # Handle status transitions
            if old_status != order.status:
                if order.status == 'confirmed':
                    order.confirmed_at = timezone.now()
                elif order.status == 'delivered':
                    order.delivered_at = timezone.now()
                order.save()
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order
        """
        order = self.get_object()
        
        if not order.can_cancel():
            return Response(
                {"error": "This order cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        order.status = 'cancelled'
        order.cancellation_reason = reason
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """
        Refund an order
        """
        order = self.get_object()
        
        if not order.can_refund():
            return Response(
                {"error": "This order cannot be refunded."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        order.status = 'refunded'
        order.payment_status = 'refunded'
        order.refund_reason = reason
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get order statistics
        """
        queryset = self.get_queryset()
        
        total_orders = queryset.count()
        pending_orders = queryset.filter(status='pending').count()
        completed_orders = queryset.filter(status='delivered').count()
        cancelled_orders = queryset.filter(status='cancelled').count()
        
        # Calculate revenue
        total_revenue = queryset.filter(
            status='delivered',
            payment_status='paid'
        ).aggregate(
            total=models.Sum('total')
        )['total'] or 0
        
        return Response({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue,
            'orders_last_7_days': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'orders_last_30_days': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
        })
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get current user's active orders
        """
        active_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'in_transit']
        orders = self.get_queryset().filter(status__in=active_statuses)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """
        Change order status with validation and history tracking
        """
        order = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        if not new_status:
            return Response(
                {"error": "New status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order.change_status(new_status, user=request.user, notes=notes)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """
        Get the status change history for an order
        """
        order = self.get_object()
        history = order.status_history.all()
        serializer = OrderStatusHistorySerializer(history, many=True)
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

class ReturnRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing return requests
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ReturnRequest.objects.prefetch_related(
            'items',
            'items__order_item',
            'items__order_item__product'
        )
        
        if user.is_staff:
            # Staff can see all return requests
            pass
        else:
            # Regular users can only see their own return requests
            queryset = queryset.filter(customer=user)
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReturnRequestCreateSerializer
        elif self.action in ['approve', 'reject']:
            return ReturnRequestReviewSerializer
        return ReturnRequestSerializer
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a return request
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff members can approve return requests"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return_request = self.get_object()
        
        try:
            refund_amount = request.data.get('refund_amount')
            admin_notes = request.data.get('admin_notes', '')
            
            if not refund_amount:
                return Response(
                    {"error": "Refund amount is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return_request.approve(
                reviewed_by=request.user,
                refund_amount=refund_amount,
                admin_notes=admin_notes
            )
            
            serializer = ReturnRequestSerializer(return_request)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a return request
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff members can reject return requests"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return_request = self.get_object()
        
        try:
            rejection_reason = request.data.get('rejection_reason')
            admin_notes = request.data.get('admin_notes', '')
            
            if not rejection_reason:
                return Response(
                    {"error": "Rejection reason is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return_request.reject(
                reviewed_by=request.user,
                rejection_reason=rejection_reason,
                admin_notes=admin_notes
            )
            
            serializer = ReturnRequestSerializer(return_request)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete_refund(self, request, pk=None):
        """
        Mark a return request as refunded
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff members can complete refunds"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return_request = self.get_object()
        
        try:
            return_request.complete_refund()
            serializer = ReturnRequestSerializer(return_request)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_by_product(request):
    """
    Get sales report aggregated by product
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    
    data = SalesReportGenerator.get_sales_by_product(start_date, end_date)
    return Response(list(data))

@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_by_date(request):
    """
    Get sales report aggregated by date
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    group_by = request.query_params.get('group_by', 'day')
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    
    if group_by not in ['day', 'month', 'year']:
        return Response(
            {'error': 'group_by must be one of: day, month, year'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = SalesReportGenerator.get_sales_by_date(group_by, start_date, end_date)
    return Response(list(data))

@api_view(['GET'])
@permission_classes([IsAdminUser])
def best_sellers(request):
    """
    Get best-selling products
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    limit = int(request.query_params.get('limit', 10))
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    
    data = SalesReportGenerator.get_best_sellers(limit, start_date, end_date)
    return Response(list(data))

@api_view(['GET'])
@permission_classes([IsAdminUser])
def worst_sellers(request):
    """
    Get worst-selling products
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    limit = int(request.query_params.get('limit', 10))
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    
    data = SalesReportGenerator.get_worst_sellers(limit, start_date, end_date)
    return Response(list(data))

@api_view(['GET'])
@permission_classes([IsAdminUser])
def low_stock_alerts(request):
    """
    Get products with low stock
    """
    threshold = int(request.query_params.get('threshold', 10))
    data = SalesReportGenerator.get_low_stock_alerts(threshold)
    return Response(list(data))

@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_summary(request):
    """
    Get overall sales summary
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    
    data = SalesReportGenerator.get_sales_summary(start_date, end_date)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def product_performance(request, product_id):
    """
    Get detailed performance metrics for a specific product
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    
    data = SalesReportGenerator.get_product_performance_metrics(product_id, start_date, end_date)
    return Response(data) 