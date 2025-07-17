from django.db import models
from django.conf import settings
from products.models import Product
from django.core.validators import MinValueValidator
from accounts.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

class Order(models.Model):
    """
    Model for storing order information
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('preparing', _('Preparing')),
        ('ready', _('Ready for Pickup/Delivery')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('pickup', _('Pickup')),
        ('delivery', _('Delivery')),
    ]

    # Define valid status transitions
    STATUS_TRANSITIONS = {
        'pending': ['processing', 'cancelled'],
        'processing': ['preparing', 'cancelled'],
        'preparing': ['ready', 'cancelled'],
        'ready': ['shipped', 'delivered', 'cancelled'],
        'shipped': ['delivered', 'cancelled'],
        'delivered': ['refunded'],
        'cancelled': [],  # No further transitions allowed
        'refunded': [],   # No further transitions allowed
    }

    # Status change messages
    STATUS_CHANGE_MESSAGES = {
        'pending': 'Order received and pending processing',
        'processing': 'Order is being processed',
        'preparing': 'Order is being prepared',
        'ready': 'Order is ready for pickup/delivery',
        'shipped': 'Order has been shipped',
        'delivered': 'Order has been delivered',
        'cancelled': 'Order has been cancelled',
        'refunded': 'Order has been refunded',
    }

    # Core fields
    # customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, default='delivery')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Financial information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Delivery information
    delivery_address = models.TextField(null=True, blank=True)
    delivery_notes = models.TextField(null=True, blank=True)
    
    # Additional information
    special_instructions = models.TextField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    refund_reason = models.TextField(null=True, blank=True)

    # Add coupon fields
    # coupon = models.ForeignKey(
    #     'coupons.Coupon',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='orders'
    # )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # models.Index(fields=['-created_at']),
            # models.Index(fields=['order_number']),
            # models.Index(fields=['status']),
            # models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.customer.username}"

    def calculate_total(self):
        """
        Calculate order total including items, tax, and delivery fee
        """
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax = self.subtotal * 0.1  # 10% tax rate
        self.total = self.subtotal + self.tax + self.delivery_fee
        return self.total

    def can_cancel(self):
        """
        Check if order can be cancelled
        """
        return self.status in ['pending', 'processing']

    def can_refund(self):
        """
        Check if order can be refunded
        """
        return self.status == 'delivered' and self.payment_status == 'paid'

    def can_transition_to(self, new_status):
        """
        Check if the order can transition to the new status
        """
        return new_status in self.STATUS_TRANSITIONS.get(self.status, [])

    def get_valid_status_transitions(self):
        """
        Get list of valid status transitions from current status
        """
        return self.STATUS_TRANSITIONS.get(self.status, [])

    def get_status_message(self):
        """
        Get the message associated with the current status
        """
        return self.STATUS_CHANGE_MESSAGES.get(self.status, '')

    def change_status(self, new_status, user=None, notes=None):
        """
        Change the order status with validation and tracking
        """
        if not self.can_transition_to(new_status):
            valid_transitions = self.get_valid_status_transitions()
            raise ValueError(
                f"Invalid status transition. Current: {self.status}. "
                f"Requested: {new_status}. Valid transitions: {', '.join(valid_transitions)}"
            )

        old_status = self.status
        self.status = new_status

        # Update timestamps based on status
        now = timezone.now()
        if new_status == 'processing':
            self.processing_started_at = now
        elif new_status == 'shipped':
            self.shipped_at = now
        elif new_status == 'delivered':
            self.delivered_at = now
        elif new_status == 'cancelled':
            self.cancelled_at = now
        elif new_status == 'refunded':
            self.refunded_at = now

        # Create status history entry
        OrderStatusHistory.objects.create(
            order=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            notes=notes
        )

        self.save()
        return True

    @property
    def total_after_discount(self):
        """
        Calculate total after applying coupon discount
        """
        return max(0, self.total - self.discount_amount)

    def apply_coupon(self, coupon):
        """
        Apply a coupon to the order
        """
        if not coupon.is_valid(
            user=self.customer,
            cart_value=self.total,
            order_items=self.items.all()
        ):
            raise ValidationError("Coupon is not valid for this order")
        
        self.coupon = coupon
        self.discount_amount = coupon.calculate_discount(self.items.all())
        self.save()
        
        # Mark coupon as used
        coupon.mark_as_used(self.customer)

    def remove_coupon(self):
        """
        Remove the applied coupon
        """
        self.coupon = None
        self.discount_amount = 0
        self.save()
        
    def pay(self):
        if self.payment_status == 'paid':
            raise ValueError('Order is already paid')
        
        from .models import Wallet, Transaction
        
        wallet, _ = Wallet.objects.get_or_create(user=self.customer)
        if wallet.balance < self.total_amount:
            raise ValueError('Insufficient funds')
        wallet.balance -= self.total_amount
        wallet.save()
        
        Transaction.objects.create(
            wallet=wallet,
            T_type='purchase',
            amount=self.total_amount,
            description=f'Order #{self.id}'
        )
        
        self.payment_status = 'paid'
        self.save()
        
        

class OrderItem(models.Model):
    """
    Model for storing order item information
    """
    # order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['id']
        indexes = [
            # models.Index(fields=['order', 'product']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.order_number}"

    def get_total(self):
        """
        Calculate total price for this item
        """
        return self.quantity * self.unit_price

class Cart(models.Model):
    """
    Shopping Cart model for storing items before checkout
    """
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.customer.username}"
    
    @property
    def total(self):
        """
        Calculate the total for all items in the cart
        """
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def item_count(self):
        """
        Get the total number of items in the cart
        """
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """
    CartItem model for individual items in a cart
    """
    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # class Meta:
        # unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        """
        Calculate the subtotal for this cart item
        """
        return self.quantity  # fallback: just quantity if product missing
    pass

class OrderStatusHistory(models.Model):
    """
    Model to track order status changes
    """
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    # changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-changed_at']
        indexes = [
            # models.Index(fields=['order', '-changed_at']),
        ]

    def __str__(self):
        return f"{self.order.order_number}: {self.old_status} → {self.new_status}"

class ReturnRequest(models.Model):
    """
    Model for managing return/refund requests
    """
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('approved', _('Approved')),
        ('processing', _('Processing Return')),
        ('completed', _('Refund Completed')),
        ('rejected', _('Rejected')),
    ]

    RETURN_TYPE_CHOICES = [
        ('refund', _('Refund Only')),
        ('return', _('Return Items')),
        ('return_refund', _('Return and Refund')),
    ]

    REASON_CHOICES = [
        ('damaged', _('Item Damaged/Defective')),
        ('wrong_item', _('Wrong Item Received')),
        ('not_satisfied', _('Not Satisfied')),
        ('size_issue', _('Size/Fit Issue')),
        ('quality_issue', _('Quality Issue')),
        ('other', _('Other')),
    ]

    # Core fields
    # order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='return_requests')
    # customer = models.ForeignKey(User, on_delete=models.PROTECT)
    return_type = models.CharField(max_length=20, choices=RETURN_TYPE_CHOICES)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Details
    description = models.TextField(help_text=_("Detailed explanation of the return/refund request"))
    proof_images = models.JSONField(default=list, blank=True, 
                                  help_text=_("List of image URLs as proof"))
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # reviewed_by = models.ForeignKey(
    #     User, 
    #     on_delete=models.SET_NULL, 
    #     null=True, 
    #     related_name='reviewed_returns'
    # )
    
    # Review details
    admin_notes = models.TextField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    refund_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # models.Index(fields=['-created_at']),
            # models.Index(fields=['status']),
            # models.Index(fields=['customer']),
            # models.Index(fields=['order']),
        ]

    def __str__(self):
        return f"Return Request #{self.id} for Order {self.order.order_number}"

    def can_review(self):
        """
        Check if the return request can be reviewed
        """
        return self.status == 'pending'

    def can_process(self):
        """
        Check if the return request can be processed
        """
        return self.status == 'approved'

    def approve(self, reviewed_by, refund_amount=None, admin_notes=None):
        """
        Approve the return request
        """
        if not self.can_review():
            raise ValueError("This return request cannot be approved")

        self.status = 'approved'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.refund_amount = refund_amount
        self.admin_notes = admin_notes
        self.save()

        # If it's refund only, complete it immediately
        if self.return_type == 'refund':
            self.complete_refund()

    def reject(self, reviewed_by, rejection_reason, admin_notes=None):
        """
        Reject the return request
        """
        if not self.can_review():
            raise ValueError("This return request cannot be rejected")

        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.rejection_reason = rejection_reason
        self.admin_notes = admin_notes
        self.save()

    def complete_refund(self):
        """
        Complete the refund process
        """
        if self.status != 'approved' and self.status != 'processing':
            raise ValueError("Cannot complete refund for non-approved request")

        self.status = 'completed'
        self.save()

        # Update order status
        self.order.status = 'refunded'
        self.order.payment_status = 'refunded'
        self.order.refund_reason = f"Return Request #{self.id}"
        self.order.save()

class ReturnItem(models.Model):
    """
    Model for individual items in a return request
    """
    # return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name='items')
    # order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason = models.CharField(max_length=20, choices=ReturnRequest.REASON_CHOICES)
    description = models.TextField(null=True, blank=True)
    condition_images = models.JSONField(default=list, blank=True, 
                                      help_text=_("List of image URLs showing item condition"))

    class Meta:
        ordering = ['id']
        indexes = [
            # models.Index(fields=['return_request', 'order_item']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.order_item.product.name} in Return #{self.return_request.id}"

    def clean(self):
        """
        Validate that return quantity doesn't exceed original order quantity
        """
        pass 
    
    
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Wallet for {self.user.username}"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('topup', 'Top-up'),
        ('refund', 'Refund'),
        ('purchase', 'Purchase'),
    ]
    
    # user = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    T_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.T_type} transaction for {self.user.user.username}"
    