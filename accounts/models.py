# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class User(AbstractUser):
    """
    Custom User model with additional fields
    """
    # Required fields (username, password, email are already in AbstractUser)
    # Additional fields
    image = models.ImageField(upload_to='user_images/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.username

class CustomerProfile(models.Model):
    """
    Extended profile information for customers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    preferences = models.JSONField(blank=True, null=True, default=dict)
    allergies = models.TextField(blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"

@receiver(post_save, sender=User)
def create_or_save_customer_profile(sender, instance, created, **kwargs):
    """
    Create a CustomerProfile instance when a new User is created,
    or save the existing profile when User is updated
    """
    if created:
        CustomerProfile.objects.create(user=instance)
    else:
        try:
            instance.customer_profile.save()
        except CustomerProfile.DoesNotExist:
            CustomerProfile.objects.create(user=instance)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"OTP for {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP expires after 10 minutes
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at