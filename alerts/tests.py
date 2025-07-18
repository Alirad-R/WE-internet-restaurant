from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User

class AlertsSmokeTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alertuser", password="alertpass")
        self.client.force_authenticate(user=self.user)

    def test_alerts_list(self):
        url = '/api/alerts/alerts/'
        response = self.client.get(url)
        print('alerts_list:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_alerts_create(self):
        url = '/api/alerts/alerts/'
        data = {"product_id": 1, "alert_type": "low_stock"}
        response = self.client.post(url, data, format='json')
        print('alerts_create:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_notifications_list(self):
        url = '/api/alerts/notifications/'
        response = self.client.get(url)
        print('notifications_list:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_notifications_create(self):
        url = '/api/alerts/notifications/'
        data = {"message": "Test notification"}
        response = self.client.post(url, data, format='json')
        print('notifications_create:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_metrics_popularity(self):
        url = '/api/alerts/metrics/popularity/'
        response = self.client.get(url)
        print('metrics_popularity:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_metrics_trending(self):
        url = '/api/alerts/metrics/trending/'
        response = self.client.get(url)
        print('metrics_trending:', response.status_code, response.json() if hasattr(response, 'json') else response.content)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]) 