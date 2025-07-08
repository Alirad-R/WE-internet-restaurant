from rest_framework import serializers
from .models import ProductAlert, AlertNotification
from products.models import Product

class ProductAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = ProductAlert
        fields = [
            'id',
            'product',
            'product_name',
            'alert_type',
            'alert_type_display',
            'severity',
            'severity_display',
            'message',
            'threshold_value',
            'current_value',
            'is_active',
            'created_at',
            'updated_at',
            'resolved_at',
            'resolved_by',
            'resolved_by_username',
            'resolution_notes'
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'resolved_at',
            'resolved_by',
            'resolved_by_username'
        ]

class AlertNotificationSerializer(serializers.ModelSerializer):
    alert_type = serializers.CharField(source='alert.get_alert_type_display', read_only=True)
    alert_message = serializers.CharField(source='alert.message', read_only=True)
    product_name = serializers.CharField(source='alert.product.name', read_only=True)
    product_id = serializers.IntegerField(source='alert.product.id', read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = [
            'id',
            'alert',
            'alert_type',
            'alert_message',
            'product_name',
            'product_id',
            'sent_at',
            'read_at',
            'notification_method',
            'is_successful'
        ]
        read_only_fields = [
            'sent_at',
            'read_at',
            'is_successful'
        ]

class ProductPopularityMetricsSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField()
    total_quantity_sold = serializers.IntegerField()
    avg_daily_orders = serializers.FloatField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock_turnover = serializers.FloatField()
    reorder_count = serializers.IntegerField()
    recent_orders = serializers.IntegerField(required=False)  # For trending products
    previous_orders = serializers.IntegerField(required=False)  # For trending products
    growth_rate = serializers.FloatField(required=False)  # For trending products
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'stock',
            'total_orders',
            'total_quantity_sold',
            'avg_daily_orders',
            'total_revenue',
            'stock_turnover',
            'reorder_count',
            'recent_orders',
            'previous_orders',
            'growth_rate'
        ] 