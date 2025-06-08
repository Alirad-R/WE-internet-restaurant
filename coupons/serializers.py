from rest_framework import serializers
from .models import (
    Coupon,
    CouponUsage,
    ReferralCoupon,
    CouponValidationHistory,
    CouponNotification
)
from django.utils import timezone

class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing coupons
    """
    status = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'valid_from', 'valid_until', 'max_uses', 'max_uses_per_user',
            'current_uses', 'min_order_value', 'min_order_items',
            'is_active', 'status', 'customer_tier', 'created_at'
        ]
        read_only_fields = ['current_uses', 'created_at']

class CouponCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating coupons
    """
    class Meta:
        model = Coupon
        fields = [
            'code', 'description', 'discount_type', 'discount_value',
            'valid_from', 'valid_until', 'max_uses', 'max_uses_per_user',
            'min_order_value', 'min_order_items', 'is_active',
            'customer_tier', 'applicable_products', 'applicable_categories',
            'excluded_products', 'excluded_categories', 'min_category_items',
            'combinable_with_discounts', 'combinable_with_coupons',
            'usage_interval_days', 'time_restrictions', 'seasonal_restrictions',
            'tiered_discounts'
        ]

    def validate(self, data):
        if data.get('valid_until') and data['valid_until'] <= data['valid_from']:
            raise serializers.ValidationError(
                "Valid until date must be after valid from date"
            )
        return data

class CouponUpdateSerializer(CouponCreateSerializer):
    """
    Serializer for updating coupons
    """
    code = serializers.CharField(read_only=True)

class CouponUsageSerializer(serializers.ModelSerializer):
    """
    Serializer for coupon usage history
    """
    user = serializers.StringRelatedField()
    
    class Meta:
        model = CouponUsage
        fields = ['id', 'coupon', 'user', 'used_at', 'order']

class ReferralCouponSerializer(serializers.ModelSerializer):
    """
    Serializer for referral coupons
    """
    referrer = serializers.StringRelatedField()
    
    class Meta:
        model = ReferralCoupon
        fields = [
            'id', 'base_coupon', 'referrer', 'referral_bonus',
            'max_referrals', 'current_referrals'
        ]
        read_only_fields = ['current_referrals']

class CouponValidationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for coupon validation history
    """
    class Meta:
        model = CouponValidationHistory
        fields = [
            'id', 'coupon', 'user', 'attempted_at',
            'validation_error', 'order_value', 'cart_items'
        ]

class CouponNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for coupon notifications
    """
    class Meta:
        model = CouponNotification
        fields = [
            'id', 'coupon', 'notification_type', 'user',
            'message', 'created_at', 'read_at'
        ]
        read_only_fields = ['created_at', 'read_at']

class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField()
    cart_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    cart_items = serializers.IntegerField(required=False)
    
    def validate_code(self, value):
        """
        Validate the coupon code
        """
        try:
            return Coupon.objects.get(code=value, is_active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError('Invalid or inactive coupon code') 