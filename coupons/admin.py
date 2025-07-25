from django.contrib import admin
from .models import (
    Coupon,
    CouponUsage,
    ReferralCoupon,
    CouponValidationHistory,
    CouponNotification
)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_type', 'discount_value', 'is_active',
        'valid_from', 'valid_until', 'current_uses', 'customer_tier'
    ]
    list_filter = [
        'is_active', 'discount_type', 'customer_tier',
        'created_at', 'valid_from', 'valid_until'
    ]
    search_fields = ['code', 'description']
    readonly_fields = ['current_uses', 'created_at', 'updated_at']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'code', 'description', 'discount_type', 'discount_value',
                'is_active', 'customer_tier'
            ]
        }),
        ('Validity', {
            'fields': [
                'valid_from', 'valid_until'
            ]
        }),
        ('Usage Limits', {
            'fields': [
                'max_uses', 'max_uses_per_user', 'current_uses',
                'usage_interval_days'
            ]
        }),
        ('Order Requirements', {
            'fields': [
                'min_order_value', 'min_order_items',
                'min_category_items'
            ]
        }),
        ('Product/Category Rules', {
            'fields': [
                'applicable_products', 'applicable_categories',
                'excluded_products', 'excluded_categories'
            ]
        }),
        ('Combination Rules', {
            'fields': [
                'combinable_with_discounts',
                'combinable_with_coupons'
            ]
        }),
        ('Advanced Settings', {
            'classes': ['collapse'],
            'fields': [
                'time_restrictions',
                'seasonal_restrictions',
                'tiered_discounts'
            ]
        }),
        ('Metadata', {
            'classes': ['collapse'],
            'fields': ['created_at', 'updated_at', 'created_by']
        })
    ]

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'used_at', 'order']
    list_filter = ['used_at', 'coupon']
    search_fields = ['coupon__code', 'user__username']
    readonly_fields = ['used_at']

@admin.register(ReferralCoupon)
class ReferralCouponAdmin(admin.ModelAdmin):
    list_display = [
        'referrer', 'referral_bonus',
        'max_referrals', 'current_referrals'
    ]
    list_filter = ['referrer']
    search_fields = ['referrer__username']
    readonly_fields = ['current_referrals']

@admin.register(CouponValidationHistory)
class CouponValidationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'coupon', 'user', 'attempted_at',
        'validation_error'
    ]
    list_filter = ['attempted_at', 'validation_error']
    search_fields = ['coupon__code', 'user__username']
    readonly_fields = ['attempted_at']

@admin.register(CouponNotification)
class CouponNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'coupon', 'notification_type', 'user',
        'created_at', 'read_at'
    ]
    list_filter = ['notification_type', 'created_at', 'read_at']
    search_fields = ['coupon__code', 'user__username', 'message']
    readonly_fields = ['created_at', 'read_at'] 