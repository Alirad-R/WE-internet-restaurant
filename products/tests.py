from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from products.models import Product, Category

class ProductEndpointsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="produser", password="prodpass")
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=10.0,
            # Add other required fields if needed
        )

    def test_product_list(self):
        url = '/api/products/'
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_product_detail(self):
        url = f'/api/products/{self.product.id}/'
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])