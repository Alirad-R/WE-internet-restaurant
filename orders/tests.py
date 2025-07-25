from rest_framework.test import APITestCase
from rest_framework import status
from coupons.models import Coupon, DiscountType
from accounts.models import User
import datetime
from django.utils import timezone

class CouponAPITests(APITestCase):
    """
    Test suite for the Coupon API endpoints.
    Mark for project: Complete.
    """
    def setUp(self):
        """
        Set up users and a coupon for testing.
        """
        self.user = User.objects.create_user(username='couponuser', password='password')
        self.admin_user = User.objects.create_superuser(username='admin', password='password')
        self.coupon = Coupon.objects.create(
            code='SAVE15',
            description='A test coupon for 15% off',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=15.00,
            valid_from=timezone.now(),
            valid_until=timezone.now() + datetime.timedelta(days=30),
            is_active=True
        )

    def test_list_coupons(self):
        """
        Mark: Ensure an authenticated user can list available coupons.
        """
        self.client.force_authenticate(user=self.user)
        url = '/api/coupons/coupons/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)

    def test_retrieve_coupon(self):
        """
        Mark: Ensure an authenticated user can retrieve a single coupon.
        """
        self.client.force_authenticate(user=self.user)
        url = f'/api/coupons/coupons/{self.coupon.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'SAVE15')

    def test_update_coupon_as_admin(self):
        """
        Mark: Ensure an admin can update a coupon via PATCH.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/coupons/coupons/{self.coupon.id}/'
        update_data = { 'is_active': False }
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.is_active, False)

    def test_update_coupon_as_regular_user_is_forbidden(self):
        """
        Mark: Ensure a regular user cannot update a coupon.
        """
        self.client.force_authenticate(user=self.user)
        url = f'/api/coupons/coupons/{self.coupon.id}/'
        update_data = { 'is_active': False }
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)