from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User

class CouponsSmokeTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="couponuser", password="couponpass")
        self.client.force_authenticate(user=self.user)

    def test_coupons_list(self):
        url = '/api/coupons/coupons/'
        response = self.client.get(url)
        print('coupons_list:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_coupons_create(self):
        url = '/api/coupons/coupons/'
        data = {"code": "TESTCOUPON", "discount": 10}
        response = self.client.post(url, data, format='json')
        print('coupons_create:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_referral_coupons_list(self):
        url = '/api/coupons/referral-coupons/'
        response = self.client.get(url)
        print('referral_coupons_list:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_referral_coupons_create(self):
        url = '/api/coupons/referral-coupons/'
        data = {"code": "REFERRAL1", "discount": 5}
        response = self.client.post(url, data, format='json')
        print('referral_coupons_create:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]) 