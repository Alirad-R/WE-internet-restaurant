from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User

class AuthEndpointsTest(APITestCase):
    def setUp(self):
        # We need a pre-existing user to test login and profile updates
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strongpassword123',
            'first_name': 'OriginalFirst',
            'last_name': 'OriginalLast'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_registration_success(self):
        """
        Ensure a new user can be registered with valid data.
        """
        url = reverse('users-list') # Correct URL is /api/auth/users/
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'anotherpassword456',
            'password2': 'anotherpassword456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_user_registration_fails_if_passwords_mismatch(self):
        """
        Ensure registration fails if the passwords do not match.
        """
        url = reverse('users-list')
        data = {
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password': 'password1',
            'password2': 'password2'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """
        Ensure a registered user can log in with correct credentials.
        """
        url = reverse('login') # Correct URL is /api/auth/login/
        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_fails_with_wrong_password(self):
        """
        Ensure login fails if the password is incorrect.
        """
        url = reverse('login')
        data = {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_update_own_profile(self):
        """
        Mark: Ensure an authenticated user can update their own profile via PUT.
        """
        # Log the user in to make authenticated requests
        self.client.force_authenticate(user=self.user)

        # Get the URL for the user profile endpoint
        url = reverse('user-profile') # This corresponds to /api/auth/profile/

        # Define the data we want to update
        updated_data = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast'
        }

        # Make the PUT request
        response = self.client.put(url, updated_data, format='json')

        # 1. Check that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Refresh the user object from the database to get the latest data
        self.user.refresh_from_db()

        # 3. Check that the first and last names were actually updated
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.last_name, 'UpdatedLast')