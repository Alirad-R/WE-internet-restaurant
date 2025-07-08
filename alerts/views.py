from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import ProductAlert, AlertNotification
from .services import ProductAlertService
from .serializers import (
    ProductAlertSerializer,
    AlertNotificationSerializer,
    ProductPopularityMetricsSerializer
)

class ProductAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product alerts
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ProductAlertSerializer
    
    def get_queryset(self):
        queryset = ProductAlert.objects.select_related('product', 'resolved_by')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by alert type
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve an alert
        """
        alert = self.get_object()
        notes = request.data.get('notes', '')
        
        alert.resolve(request.user, notes)
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_low_stock(self, request):
        """
        Manually trigger low stock check
        """
        threshold = int(request.data.get('threshold', 10))
        alerts = ProductAlertService.check_low_stock_products(threshold)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_high_demand(self, request):
        """
        Manually trigger high demand check
        """
        order_threshold = int(request.data.get('order_threshold', 10))
        time_window_days = int(request.data.get('time_window_days', 7))
        
        alerts = ProductAlertService.check_high_demand_products(
            order_threshold=order_threshold,
            time_window_days=time_window_days
        )
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

class AlertNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing alert notifications
    """
    serializer_class = AlertNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AlertNotification.objects.filter(
            user=self.request.user
        ).select_related(
            'alert',
            'alert__product'
        ).order_by('-sent_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all notifications as read
        """
        ProductAlertService.mark_notifications_as_read(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read
        """
        notification = self.get_object()
        notification.mark_as_read()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def product_popularity_metrics(request):
    """
    Get comprehensive popularity metrics for all products
    """
    days = int(request.query_params.get('days', 30))
    metrics = ProductAlertService.get_product_popularity_metrics(days=days)
    serializer = ProductPopularityMetricsSerializer(metrics, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def trending_products(request):
    """
    Get products with rapidly increasing popularity
    """
    days = int(request.query_params.get('days', 7))
    min_orders = int(request.query_params.get('min_orders', 5))
    products = ProductAlertService.get_trending_products(days=days, min_orders=min_orders)
    serializer = ProductPopularityMetricsSerializer(products, many=True)
    return Response(serializer.data) 