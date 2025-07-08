from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Coupon, CouponNotification

@shared_task
def check_expiring_coupons():
    """
    Check for coupons that are about to expire and notify users
    """
    # Get coupons expiring in the next 7 days
    expiry_threshold = timezone.now() + timezone.timedelta(days=7)
    expiring_coupons = Coupon.objects.filter(
        is_active=True,
        valid_until__lte=expiry_threshold,
        valid_until__gt=timezone.now()
    )

    for coupon in expiring_coupons:
        # Get eligible users
        users = coupon.get_eligible_users()
        
        for user in users:
            # Create notification
            notification = CouponNotification.objects.create(
                coupon=coupon,
                user=user,
                notification_type='expiring_soon',
                message=f"Your coupon {coupon.code} will expire in {(coupon.valid_until - timezone.now()).days} days!"
            )
            
            # Send email
            if user.email:
                send_mail(
                    subject=f"Your coupon {coupon.code} is expiring soon!",
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )

@shared_task
def cleanup_expired_coupons():
    """
    Deactivate expired coupons
    """
    now = timezone.now()
    expired_coupons = Coupon.objects.filter(
        is_active=True,
        valid_until__lte=now
    )
    
    for coupon in expired_coupons:
        coupon.is_active = False
        coupon.save()
        
        # Notify admin
        if coupon.created_by and coupon.created_by.email:
            send_mail(
                subject=f"Coupon {coupon.code} has expired",
                message=f"The coupon {coupon.code} has expired and been deactivated.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[coupon.created_by.email],
                fail_silently=True
            )

@shared_task
def notify_usage_limit_reached(coupon_id):
    """
    Notify when a coupon reaches its usage limit
    """
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        if coupon.created_by and coupon.created_by.email:
            send_mail(
                subject=f"Coupon {coupon.code} usage limit reached",
                message=f"The coupon {coupon.code} has reached its maximum usage limit of {coupon.max_uses}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[coupon.created_by.email],
                fail_silently=True
            )
    except Coupon.DoesNotExist:
        pass 