from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Coupon, ReferralCoupon, CouponUsage, CouponValidationHistory
from .serializers import (
    CouponSerializer,
    CouponCreateSerializer,
    CouponUpdateSerializer,
    ReferralCouponSerializer,
    CouponValidationHistorySerializer,
    CouponUsageSerializer
)

class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing coupons
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CouponCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CouponUpdateSerializer
        return CouponSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Regular users can only see active, valid coupons
            now = timezone.now()
            return queryset.filter(
                Q(is_active=True) &
                Q(valid_from__lte=now) &
                (Q(valid_until__isnull=True) | Q(valid_until__gt=now))
            )
        return queryset

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Validate a coupon for the current user
        """
        coupon = self.get_object()
        cart_value = request.data.get('cart_value')
        cart_items = request.data.get('cart_items')
        
        is_valid = coupon.is_valid(
            user=request.user,
            cart_value=cart_value,
            cart_items=cart_items
        )
        
        return Response({
            'is_valid': is_valid,
            'message': coupon._get_validation_error_message(
                request.user,
                cart_value,
                cart_items,
                None
            ) if not is_valid else 'Coupon is valid'
        })

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        Apply a coupon to the current user's cart
        """
        coupon = self.get_object()
        cart_value = request.data.get('cart_value')
        cart_items = request.data.get('cart_items')
        
        if not coupon.is_valid(request.user, cart_value, cart_items):
            return Response(
                {'error': 'Coupon is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        discount = coupon.calculate_discount(cart_items)
        coupon.mark_as_used(request.user)
        
        return Response({
            'discount': discount,
            'message': 'Coupon applied successfully'
        })

class ReferralCouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing referral coupons
    """
    queryset = ReferralCoupon.objects.all()
    serializer_class = ReferralCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(referrer=self.request.user)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        Generate a new referral coupon
        """
        referral = self.get_object()
        if referral.current_referrals >= referral.max_referrals:
            return Response(
                {'error': 'Maximum referrals reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique coupon code
        code = f"REF-{request.user.username}-{timezone.now().strftime('%y%m%d%H%M%S')}"
        
        coupon = Coupon.objects.create(
            code=code,
            discount_type='percentage',
            discount_value=referral.referral_bonus,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=30),
            max_uses=1,
            created_by=request.user
        )
        
        referral.current_referrals += 1
        referral.save()
        
        return Response({
            'coupon_code': code,
            'message': 'Referral coupon generated successfully'
        })

class CouponUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing coupon usage history
    """
    serializer_class = CouponUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Staff can see all usage history, users only see their own
        """
        queryset = CouponUsage.objects.select_related(
            'coupon',
            'user',
            'order'
        )
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset 