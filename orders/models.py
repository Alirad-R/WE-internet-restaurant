from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    """
    Order model to track customer orders
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"
    
    def calculate_total(self):
        """
        Calculate the total amount for the order
        """
        return sum(item.subtotal for item in self.items.all())
    
    def save(self, *args, **kwargs):
        # Calculate total if not set
        if self.pk is None or not self.total_amount:
            if self.pk is not None:  # If the order already exists
                self.total_amount = self.calculate_total()
            else:  # New order, may not have items yet
                self.total_amount = self.total_amount or 0
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """
    OrderItem model for individual items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        """
        Calculate the subtotal for this item
        """
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        # Set unit price from product if not set
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)

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
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        """
        Calculate the subtotal for this cart item
        """
        return self.quantity * self.product.price 