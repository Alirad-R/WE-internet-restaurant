from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, ReferralCouponViewSet

router = DefaultRouter()
router.register(r'coupons', CouponViewSet)
router.register(r'referral-coupons', ReferralCouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 