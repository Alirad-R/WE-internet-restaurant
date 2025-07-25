from rest_framework.test import APITestCase
from rest_framework import status
from .models import ProductAlert, AlertType
from accounts.models import User
from products.models import Product, Category

class AlertAPITests(APITestCase):
    """
    Test suite for the Alert API endpoints.
    Mark for project: Complete.
    """
    def setUp(self):
        """
        Set up objects needed for alert testing.
        """
        self.user = User.objects.create_user(username='alertuser', password='password')
        self.admin_user = User.objects.create_superuser(username='admin', password='password')

        # An Alert is tied to a Product, so we must create one
        category = Category.objects.create(name='Test Category for Alerts')
        product = Product.objects.create(
            name='Test Product for Alerts',
            price=25.00,
            category=category,
            is_available=True
        )

        self.alert = ProductAlert.objects.create(
            product=product,
            alert_type=AlertType.LOW_STOCK,
            message='Stock is running low!',
            threshold_value=10,
            current_value=8,
            is_active=True
        )

    def test_list_alerts(self):
        """
        Mark: Ensure a logged-in user can see alerts.
        """
        self.client.force_authenticate(user=self.admin_user) # Assuming admins see all alerts
        url = '/api/alerts/alerts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)

    def test_retrieve_alert(self):
        """
        Mark: Ensure a logged-in user can retrieve a single alert.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/alerts/alerts/{self.alert.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Stock is running low!')

    def test_resolve_alert_as_admin(self):
        """
        Mark: Ensure an admin can resolve an alert via PATCH.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/alerts/alerts/{self.alert.id}/'
        update_data = { 'is_active': False }
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.is_active, False)

    def test_resolve_alert_as_regular_user_is_forbidden(self):
        """
        Mark: Ensure a regular user cannot resolve an alert.
        """
        self.client.force_authenticate(user=self.user)
        url = f'/api/alerts/alerts/{self.alert.id}/'
        update_data = { 'is_active': False }
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)