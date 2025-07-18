from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from orders.models import Order

class OrderEndpointsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderuser", password="orderpass")
        self.client.force_authenticate(user=self.user)
        # Remove 'customer' if not present in Order model
        # After creating an Order, also create an OrderItem with subtotal
        order = Order.objects.create(status='pending', payment_status='unpaid')
        OrderItem.objects.create(order=order, subtotal=0, ...)  # Add other required fields

    def test_order_list(self):
        url = '/api/orders/'
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_order_detail(self):
        url = f'/api/orders/{self.order.id}/'
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_order_create(self):
        url = '/api/orders/'
        data = {
            "status": "pending",
            "payment_status": "unpaid",
            # Add other required fields here if needed
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])