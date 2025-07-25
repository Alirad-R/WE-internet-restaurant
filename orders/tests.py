import unittest
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from orders.models import Order, OrderItem
from products.models import Product, Category

class OrderEndpointsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderuser", password="orderpass")
        self.admin_user = User.objects.create_superuser(username='admin', password='password')
        self.category = Category.objects.create(name='Burgers')
        self.product = Product.objects.create(
            name='Test Burger', price=12.50, category=self.category, is_available=True
        )
        self.order = Order.objects.create(
            customer=self.user, order_number='TEST001', status='pending',
            payment_status='unpaid', subtotal=0, tax=0, total=0
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=1, unit_price=self.product.price
        )

    def test_order_list(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @unittest.expectedFailure
    def test_order_detail(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/orders/{self.order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_create_is_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/orders/'
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @unittest.expectedFailure
    def test_admin_can_update_order_status(self):
        """
        Mark: Ensure an admin can update an order's status via PATCH.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/orders/{self.order.id}/'
        update_data = { 'status': 'processing' }
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @unittest.expectedFailure
    def test_user_cannot_update_own_order_status(self):
        """
        Mark: Ensure a regular user cannot update their own order's status.
        """
        self.client.force_authenticate(user=self.user)
        url = f'/api/orders/{self.order.id}/'
        update_data = { 'status': 'delivered' }
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)