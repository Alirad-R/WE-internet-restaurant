from django.db import models
from django.conf import settings
from products.models import Product

class AlertType(models.TextChoices):
    LOW_STOCK = 'low_stock', 'Low Stock'
    OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'
    HIGH_DEMAND = 'high_demand', 'High Demand'
    PRICE_CHANGE = 'price_change', 'Price Change'

class AlertSeverity(models.TextChoices):
    INFO = 'info', 'Information'
    WARNING = 'warning', 'Warning'
    CRITICAL = 'critical', 'Critical'

class ProductAlert(models.Model):
    """
    Model for tracking product-related alerts
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices
    )
    severity = models.CharField(
        max_length=10,
        choices=AlertSeverity.choices,
        default=AlertSeverity.WARNING
    )
    message = models.TextField()
    threshold_value = models.IntegerField(
        help_text="Threshold that triggered the alert (e.g., stock level)"
    )
    current_value = models.IntegerField(
        help_text="Current value when alert was created"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'alert_type', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name}"

    def resolve(self, user, notes=''):
        """
        Mark the alert as resolved
        """
        from django.utils import timezone
        self.is_active = False
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes
        self.save()

class AlertNotification(models.Model):
    """
    Model for tracking alert notifications sent to users
    """
    alert = models.ForeignKey(
        ProductAlert,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alert_notifications'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    notification_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('in_app', 'In-App Notification'),
            ('sms', 'SMS'),
        ]
    )
    is_successful = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'read_at']),
            models.Index(fields=['sent_at']),
        ]

    def mark_as_read(self):
        """
        Mark the notification as read
        """
        from django.utils import timezone
        self.read_at = timezone.now()
        self.save() 