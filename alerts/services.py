from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import F, Q, Count, Avg, Sum, FloatField, ExpressionWrapper
from products.models import Product
from .models import ProductAlert, AlertType, AlertSeverity, AlertNotification
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class ProductAlertService:
    """
    Service class for managing product alerts and notifications
    """
    
    @classmethod
    def check_low_stock_products(cls, threshold=10):
        """
        Check for products with low stock and create alerts
        """
        low_stock_products = Product.objects.filter(
            Q(stock__lte=threshold) & 
            Q(is_active=True) &
            ~Q(alerts__alert_type=AlertType.LOW_STOCK, alerts__is_active=True)
        )
        
        alerts_created = []
        for product in low_stock_products:
            alert = ProductAlert.objects.create(
                product=product,
                alert_type=AlertType.LOW_STOCK,
                severity=AlertSeverity.WARNING if product.stock > 0 else AlertSeverity.CRITICAL,
                message=f"Product '{product.name}' is running low on stock. Current stock: {product.stock}",
                threshold_value=threshold,
                current_value=product.stock
            )
            alerts_created.append(alert)
            cls.notify_staff_about_alert(alert)
        
        return alerts_created

    @classmethod
    def check_high_demand_products(cls, order_threshold=10, time_window_days=7):
        """
        Check for products with unusually high demand
        """
        from django.db.models import Count
        
        time_threshold = timezone.now() - timedelta(days=time_window_days)
        
        # First get products without active high demand alerts
        products_without_alerts = Product.objects.filter(
            ~Q(alerts__alert_type=AlertType.HIGH_DEMAND, alerts__is_active=True)
        )
        
        # Then filter for high demand among these products
        high_demand_products = products_without_alerts.filter(
            orderitem__order__created_at__gte=time_threshold
        ).annotate(
            order_count=Count('orderitem')
        ).filter(
            order_count__gte=order_threshold
        )
        
        alerts_created = []
        for product in high_demand_products:
            alert = ProductAlert.objects.create(
                product=product,
                alert_type=AlertType.HIGH_DEMAND,
                severity=AlertSeverity.WARNING,
                message=f"Product '{product.name}' is in high demand. {product.order_count} orders in the last {time_window_days} days.",
                threshold_value=order_threshold,
                current_value=product.order_count
            )
            alerts_created.append(alert)
            cls.notify_staff_about_alert(alert)
        
        return alerts_created

    @classmethod
    def get_product_popularity_metrics(cls, days=30):
        """
        Get comprehensive popularity metrics for products
        """
        time_threshold = timezone.now() - timedelta(days=days)
        
        return Product.objects.filter(
            is_active=True
        ).annotate(
            # Order-based metrics
            total_orders=Count(
                'orderitem__order',
                filter=Q(orderitem__order__created_at__gte=time_threshold),
                distinct=True
            ),
            total_quantity_sold=Sum(
                'orderitem__quantity',
                filter=Q(orderitem__order__created_at__gte=time_threshold)
            ),
            
            # Average daily sales
            avg_daily_orders=ExpressionWrapper(
                F('total_orders') * 1.0 / days,
                output_field=FloatField()
            ),
            
            # Revenue metrics
            total_revenue=Sum(
                F('orderitem__quantity') * F('orderitem__unit_price'),
                filter=Q(orderitem__order__created_at__gte=time_threshold)
            ),
            
            # Stock turnover rate (units sold / average stock level)
            stock_turnover=ExpressionWrapper(
                F('total_quantity_sold') * 1.0 / (F('stock') + 1),  # Add 1 to avoid division by zero
                output_field=FloatField()
            ),
            
            # Reorder frequency
            reorder_count=Count(
                'orderitem__order',
                filter=Q(
                    orderitem__order__created_at__gte=time_threshold,
                    orderitem__order__customer__in=models.Subquery(
                        models.Q(orderitem__order__customer__in=models.Q(orderitem__order__created_at__lt=F('orderitem__order__created_at')))
                    )
                ),
                distinct=True
            )
        ).order_by('-total_orders')

    @classmethod
    def get_trending_products(cls, days=7, min_orders=5):
        """
        Get products with rapidly increasing popularity
        """
        now = timezone.now()
        recent_threshold = now - timedelta(days=days)
        previous_threshold = recent_threshold - timedelta(days=days)
        
        return Product.objects.filter(
            is_active=True
        ).annotate(
            # Recent period metrics
            recent_orders=Count(
                'orderitem__order',
                filter=Q(orderitem__order__created_at__gte=recent_threshold),
                distinct=True
            ),
            # Previous period metrics
            previous_orders=Count(
                'orderitem__order',
                filter=Q(
                    orderitem__order__created_at__gte=previous_threshold,
                    orderitem__order__created_at__lt=recent_threshold
                ),
                distinct=True
            )
        ).annotate(
            growth_rate=ExpressionWrapper(
                (F('recent_orders') - F('previous_orders')) * 100.0 / (F('previous_orders') + 1),
                output_field=FloatField()
            )
        ).filter(
            recent_orders__gte=min_orders
        ).order_by('-growth_rate')

    @classmethod
    def notify_staff_about_alert(cls, alert):
        """
        Send notifications to staff members about the alert
        """
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        
        for user in staff_users:
            # Create in-app notification
            notification = AlertNotification.objects.create(
                alert=alert,
                user=user,
                notification_method='in_app'
            )
            
            # Send email notification
            try:
                subject = f"Product Alert: {alert.get_alert_type_display()}"
                context = {
                    'user': user,
                    'alert': alert,
                    'product': alert.product
                }
                
                html_message = render_to_string('alerts/email/alert_notification.html', context)
                plain_message = render_to_string('alerts/email/alert_notification.txt', context)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message
                )
                
                notification.is_successful = True
                notification.save()
                
            except Exception as e:
                notification.is_successful = False
                notification.error_message = str(e)
                notification.save()

    @classmethod
    def get_active_alerts(cls, alert_type=None, severity=None):
        """
        Get active alerts with optional filtering
        """
        queryset = ProductAlert.objects.filter(is_active=True)
        
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        if severity:
            queryset = queryset.filter(severity=severity)
        
        return queryset.select_related('product')

    @classmethod
    def get_unread_notifications(cls, user):
        """
        Get unread notifications for a user
        """
        return AlertNotification.objects.filter(
            user=user,
            read_at__isnull=True
        ).select_related('alert', 'alert__product')

    @classmethod
    def mark_notifications_as_read(cls, user, notification_ids=None):
        """
        Mark notifications as read for a user
        """
        queryset = AlertNotification.objects.filter(user=user, read_at__isnull=True)
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        return queryset.update(read_at=timezone.now()) 