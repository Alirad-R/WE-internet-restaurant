from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from products.models import Product, Category
from django.db.models import Sum, Count, Q

class DiscountType(models.TextChoices):
    PERCENTAGE = 'percentage', 'Percentage'
    FIXED = 'fixed', 'Fixed Amount'
    BUY_X_GET_Y = 'buy_x_get_y', 'Buy X Get Y'
    TIERED = 'tiered', 'Tiered Discount'  # New type for tiered discounts

class CouponStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    DEPLETED = 'depleted', 'Depleted'
    CANCELLED = 'cancelled', 'Cancelled'
    SCHEDULED = 'scheduled', 'Scheduled'  # New status for future coupons

class CustomerTier(models.TextChoices):
    ALL = 'all', 'All Customers'
    NEW = 'new', 'New Customers'
    REGULAR = 'regular', 'Regular Customers'
    VIP = 'vip', 'VIP Customers'

class Coupon(models.Model):
    """
    Enhanced model for discount coupons with advanced rules and restrictions
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique coupon code"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the coupon and its terms"
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Discount value (percentage or fixed amount)"
    )
    
    # Validity period
    valid_from = models.DateTimeField(
        default=timezone.now,
        help_text="Start date of coupon validity"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End date of coupon validity (optional)"
    )
    
    # Usage limits
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this coupon can be used (optional)"
    )
    max_uses_per_user = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of times a single user can use this coupon"
    )
    current_uses = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this coupon has been used"
    )
    
    # Minimum requirements
    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum order value required to use this coupon"
    )
    min_order_items = models.PositiveIntegerField(
        default=1,
        help_text="Minimum number of items required in cart"
    )
    
    # Restrictions
    is_active = models.BooleanField(default=True)
    is_one_time_use = models.BooleanField(
        default=False,
        help_text="If True, coupon can only be used once per user"
    )
    applies_to_discounted_items = models.BooleanField(
        default=False,
        help_text="If True, coupon can be applied to already discounted items"
    )
    
    # Product/Category specific rules
    applicable_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='applicable_coupons',
        help_text="Specific products this coupon applies to (empty means all products)"
    )
    applicable_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='applicable_coupons',
        help_text="Specific categories this coupon applies to (empty means all categories)"
    )
    
    # Buy X Get Y specific fields
    buy_x_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of items to buy (for Buy X Get Y)"
    )
    get_y_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of items to get free (for Buy X Get Y)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_coupons'
    )

    # New fields for advanced conditions
    customer_tier = models.CharField(
        max_length=20,
        choices=CustomerTier.choices,
        default=CustomerTier.ALL,
        help_text="Customer tier this coupon is applicable to"
    )
    
    min_customer_orders = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum number of previous orders required"
    )
    
    max_customer_orders = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of previous orders allowed"
    )
    
    min_customer_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum amount customer must have spent historically"
    )
    
    excluded_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='excluded_coupons',
        help_text="Products that cannot be discounted with this coupon"
    )
    
    excluded_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='excluded_coupons',
        help_text="Categories that cannot be discounted with this coupon"
    )
    
    min_category_items = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum number of items required from applicable categories"
    )
    
    combinable_with_discounts = models.BooleanField(
        default=False,
        help_text="Whether this coupon can be combined with other discounts"
    )
    
    combinable_with_coupons = models.BooleanField(
        default=False,
        help_text="Whether this coupon can be combined with other coupons"
    )
    
    usage_interval_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum days required between uses by the same user"
    )
    
    time_restrictions = models.JSONField(
        null=True,
        blank=True,
        help_text="Time-based restrictions (e.g., specific days or hours)"
    )
    
    seasonal_restrictions = models.JSONField(
        null=True,
        blank=True,
        help_text="Seasonal restrictions (e.g., specific months or holidays)"
    )
    
    tiered_discounts = models.JSONField(
        null=True,
        blank=True,
        help_text="Tiered discount rules (e.g., spend more save more)"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['valid_from', 'valid_until']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"

    @property
    def status(self):
        """
        Get the current status of the coupon
        """
        now = timezone.now()
        
        if not self.is_active:
            return CouponStatus.CANCELLED
        
        if self.valid_until and now > self.valid_until:
            return CouponStatus.EXPIRED
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return CouponStatus.DEPLETED
        
        if now < self.valid_from:
            return CouponStatus.INACTIVE
        
        return CouponStatus.ACTIVE

    def log_validation_failure(self, user, error, order_value=None, cart_items=None):
        """
        Log a failed validation attempt
        """
        CouponValidationHistory.objects.create(
            coupon=self,
            user=user,
            validation_error=error,
            order_value=order_value,
            cart_items=cart_items
        )

    def create_notification(self, user, notification_type, message):
        """
        Create a notification for the coupon
        """
        return CouponNotification.objects.create(
            coupon=self,
            user=user,
            notification_type=notification_type,
            message=message
        )

    def check_and_notify_expiration(self):
        """
        Check if coupon is expiring soon and notify relevant users
        """
        if not self.valid_until:
            return
            
        days_until_expiry = (self.valid_until - timezone.now()).days
        
        if days_until_expiry <= 7:  # Notify when 7 or fewer days remain
            users_to_notify = self.get_eligible_users()
            
            for user in users_to_notify:
                self.create_notification(
                    user=user,
                    notification_type='expiring_soon',
                    message=f"Your coupon {self.code} will expire in {days_until_expiry} days!"
                )

    def get_eligible_users(self):
        """
        Get users eligible for this coupon based on tier and history
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users = User.objects.filter(is_active=True)
        
        if self.customer_tier != CustomerTier.ALL:
            # Filter based on tier requirements
            if self.customer_tier == CustomerTier.NEW:
                users = users.annotate(
                    order_count=Count('orders')
                ).filter(order_count=0)
            
            elif self.customer_tier == CustomerTier.REGULAR:
                users = users.annotate(
                    order_count=Count('orders'),
                    total_spent=Sum('orders__total_amount')
                ).filter(
                    order_count__gte=3,
                    total_spent__gte=100
                )
            
            elif self.customer_tier == CustomerTier.VIP:
                users = users.annotate(
                    order_count=Count('orders'),
                    total_spent=Sum('orders__total_amount')
                ).filter(
                    order_count__gte=10,
                    total_spent__gte=1000
                )
        
        # Exclude users who have already used this coupon maximum times
        if self.max_uses_per_user:
            users = users.annotate(
                usage_count=Count('coupon_usages', filter=Q(coupon_usages__coupon=self))
            ).filter(usage_count__lt=self.max_uses_per_user)
        
        return users

    def is_valid(self, user=None, cart_value=None, cart_items=None, order_items=None):
        """
        Enhanced validation with logging
        """
        try:
            is_valid = super().is_valid(user, cart_value, cart_items, order_items)
            
            if not is_valid:
                error_message = self._get_validation_error_message(
                    user, cart_value, cart_items, order_items
                )
                self.log_validation_failure(
                    user=user,
                    error=error_message,
                    order_value=cart_value,
                    cart_items=cart_items
                )
            
            return is_valid
            
        except Exception as e:
            self.log_validation_failure(
                user=user,
                error=str(e),
                order_value=cart_value,
                cart_items=cart_items
            )
            return False

    def _get_validation_error_message(self, user, cart_value, cart_items, order_items):
        """
        Get detailed validation error message
        """
        if not self.is_active:
            return "Coupon is not active"
            
        if self.status == CouponStatus.EXPIRED:
            return "Coupon has expired"
            
        if self.status == CouponStatus.DEPLETED:
            return "Coupon usage limit reached"
            
        if cart_value and cart_value < self.min_order_value:
            return f"Order value (${cart_value}) is below minimum required (${self.min_order_value})"
            
        if cart_items and len(cart_items) < self.min_order_items:
            return f"Cart has fewer items ({len(cart_items)}) than required ({self.min_order_items})"
            
        if user and not self._validate_customer_tier(user):
            return f"User does not meet {self.get_customer_tier_display()} requirements"
            
        if order_items and not self._validate_category_requirements(order_items):
            return "Category-specific requirements not met"
            
        return "General validation failure"

    def _validate_customer_tier(self, user):
        """
        Validate user's eligibility based on customer tier
        """
        if self.customer_tier == CustomerTier.ALL:
            return True
            
        from orders.models import Order
        
        total_orders = Order.objects.filter(
            customer=user,
            status='delivered'
        ).count()
        
        total_spent = Order.objects.filter(
            customer=user,
            status='delivered'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        if self.customer_tier == CustomerTier.NEW:
            return total_orders == 0
            
        elif self.customer_tier == CustomerTier.REGULAR:
            return total_orders >= 3 and total_spent >= 100
            
        elif self.customer_tier == CustomerTier.VIP:
            return total_orders >= 10 and total_spent >= 1000
            
        return False

    def _validate_order_history(self, user):
        """
        Validate user's order history requirements
        """
        if not (self.min_customer_orders or self.max_customer_orders or self.min_customer_spent):
            return True
            
        from orders.models import Order
        
        user_orders = Order.objects.filter(
            customer=user,
            status='delivered'
        )
        
        order_count = user_orders.count()
        
        if self.min_customer_orders and order_count < self.min_customer_orders:
            return False
            
        if self.max_customer_orders and order_count > self.max_customer_orders:
            return False
            
        if self.min_customer_spent:
            total_spent = user_orders.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            if total_spent < self.min_customer_spent:
                return False
        
        return True

    def _validate_usage_interval(self, user):
        """
        Validate minimum interval between uses
        """
        if not self.usage_interval_days:
            return True
            
        last_usage = CouponUsage.objects.filter(
            coupon=self,
            user=user
        ).order_by('-used_at').first()
        
        if last_usage:
            days_since_last_use = (timezone.now() - last_usage.used_at).days
            return days_since_last_use >= self.usage_interval_days
            
        return True

    def _validate_category_requirements(self, order_items):
        """
        Validate category-specific requirements
        """
        if not self.min_category_items:
            return True
            
        if not self.applicable_categories.exists():
            return True
            
        category_items = sum(
            item.quantity
            for item in order_items
            if item.product.category in self.applicable_categories.all()
        )
        
        return category_items >= self.min_category_items

    def _has_excluded_items(self, order_items):
        """
        Check if order contains excluded items
        """
        for item in order_items:
            # Check excluded products
            if self.excluded_products.filter(id=item.product.id).exists():
                return True
                
            # Check excluded categories
            if self.excluded_categories.filter(id=item.product.category_id).exists():
                return True
        
        return False

    def _validate_discount_combinations(self, order_items):
        """
        Validate discount combination rules
        """
        if self.combinable_with_discounts:
            return True
            
        # Check if any item has existing discounts
        for item in order_items:
            if item.product.is_on_sale or item.product.discount_price:
                return False
        
        return True

    def _validate_time_restrictions(self):
        """
        Validate time-based restrictions
        """
        if not self.time_restrictions:
            return True
            
        now = timezone.now()
        restrictions = self.time_restrictions
        
        # Check day of week
        if 'days' in restrictions:
            if now.strftime('%A').lower() not in restrictions['days']:
                return False
        
        # Check hour range
        if 'hours' in restrictions:
            current_hour = now.hour
            valid_hours = restrictions['hours']
            if not (valid_hours['start'] <= current_hour < valid_hours['end']):
                return False
        
        return True

    def _validate_seasonal_restrictions(self):
        """
        Validate seasonal restrictions
        """
        if not self.seasonal_restrictions:
            return True
            
        now = timezone.now()
        restrictions = self.seasonal_restrictions
        
        # Check months
        if 'months' in restrictions:
            if now.month not in restrictions['months']:
                return False
        
        # Check specific dates
        if 'dates' in restrictions:
            current_date = now.strftime('%m-%d')
            if current_date not in restrictions['dates']:
                return False
        
        return True

    def calculate_discount(self, order_items):
        """
        Enhanced discount calculation with tiered pricing
        """
        if self.discount_type != DiscountType.TIERED:
            return super().calculate_discount(order_items)
            
        if not self.tiered_discounts:
            return 0
            
        total = sum(
            item.get_total()
            for item in order_items
            if self.is_applicable_to_item(item.product)
        )
        
        # Find applicable tier
        applicable_tier = None
        for tier in sorted(self.tiered_discounts, key=lambda x: x['min_amount']):
            if total >= tier['min_amount']:
                applicable_tier = tier
            else:
                break
        
        if not applicable_tier:
            return 0
            
        if applicable_tier['type'] == 'percentage':
            return (total * applicable_tier['value']) / 100
        else:
            return applicable_tier['value']

    def is_applicable_to_item(self, product):
        """
        Check if coupon is applicable to a specific product
        """
        # If no specific products or categories are set, coupon applies to all
        if not self.applicable_products.exists() and not self.applicable_categories.exists():
            return True
        
        # Check if product is directly applicable
        if self.applicable_products.filter(id=product.id).exists():
            return True
        
        # Check if product's category is applicable
        if self.applicable_categories.filter(id=product.category_id).exists():
            return True
        
        return False

    def mark_as_used(self, user):
        """
        Mark the coupon as used by a user
        """
        self.current_uses += 1
        self.save()
        
        CouponUsage.objects.create(
            coupon=self,
            user=user
        )

class CouponUsage(models.Model):
    """
    Model to track coupon usage by users
    """
    # coupon = models.ForeignKey(
    #     Coupon,
    #     on_delete=models.CASCADE,
    #     related_name='usages'
    # )
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='coupon_usages'
    # )
    used_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        related_name='coupon_usages'
    )

    class Meta:
        ordering = ['-used_at']
        indexes = [
            # models.Index(fields=['coupon', 'user']),
            models.Index(fields=['used_at']),
        ]
        # unique_together = ['coupon', 'order']  # Prevent duplicate usage on same order

    def __str__(self):
        return f"{self.coupon.code} used by {self.user.username}"

class CouponValidationHistory(models.Model):
    """
    Track failed validation attempts and reasons
    """
    # coupon = models.ForeignKey(
    #     Coupon,
    #     on_delete=models.CASCADE,
    #     related_name='validation_history'
    # )
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='coupon_validation_history'
    # )
    attempted_at = models.DateTimeField(auto_now_add=True)
    validation_error = models.CharField(max_length=255)
    order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True
    )
    cart_items = models.JSONField(null=True)

    class Meta:
        ordering = ['-attempted_at']
        indexes = [
            # models.Index(fields=['coupon', 'user']),
            # models.Index(fields=['attempted_at']),
        ]

    def __str__(self):
        return f"{self.coupon.code} validation failed for {self.user.username}: {self.validation_error}"

class ReferralCoupon(models.Model):
    """
    Special coupons for customer referrals
    """
    # base_coupon = models.OneToOneField(
    #     Coupon,
    #     on_delete=models.CASCADE,
    #     related_name='referral_details'
    # )
    # referrer = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='created_referrals'
    # )
    referral_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Bonus amount/percentage for the referrer"
    )
    max_referrals = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of referrals allowed"
    )
    current_referrals = models.PositiveIntegerField(
        default=0,
        help_text="Number of successful referrals"
    )
    
    class Meta:
        indexes = [
            # models.Index(fields=['referrer']),
            # models.Index(fields=['base_coupon']),
        ]

    def __str__(self):
        return f"Referral coupon by {self.referrer.username}"

class CouponNotification(models.Model):
    """
    Notification system for coupon-related events
    """
    NOTIFICATION_TYPES = [
        ('expiring_soon', 'Expiring Soon'),
        ('usage_limit', 'Usage Limit Reached'),
        ('new_coupon', 'New Coupon Available'),
        ('referral_used', 'Referral Coupon Used'),
    ]

    # coupon = models.ForeignKey(
    #     Coupon,
    #     on_delete=models.CASCADE,
    #     related_name='notifications'
    # )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='coupon_notifications'
    # )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # models.Index(fields=['user', 'read_at']),
            # models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.coupon.code}" 