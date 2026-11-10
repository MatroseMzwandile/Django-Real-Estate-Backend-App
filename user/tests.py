from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAuthTests(APITestCase):
    # Enable multi-database support for test runner
    databases = {'default', 'users', 'listings'}

    def setUp(self):
        self.register_url = '/auth/user/register'
        self.login_url = '/api/token/'
        self.user_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123',
            're_password': 'password123',
            'is_realtor': 'False',
        }
        self.realtor_data = {
            'name': 'Jane Realtor',
            'email': 'jane@example.com',
            'password': 'password123',
            're_password': 'password123',
            'is_realtor': 'True',
        }

    # --- Registration Tests ---

    def test_register_regular_user_success(self):
        """Standard user registers successfully with is_realtor=False."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
        user = User.objects.get(email='john@example.com')
        self.assertFalse(user.is_realtor)

    def test_register_realtor_user_success(self):
        """Realtor registers successfully with is_realtor=True."""
        response = self.client.post(self.register_url, self.realtor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='jane@example.com').exists())
        user = User.objects.get(email='jane@example.com')
        self.assertTrue(user.is_realtor)

    def test_register_passwords_mismatch(self):
        """Registration fails when password and re_password do not match."""
        data = self.user_data.copy()
        data['re_password'] = 'mismatchpassword'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_register_password_too_short(self):
        """Registration fails when password is under 8 characters."""
        data = self.user_data.copy()
        data['password'] = 'short'
        data['re_password'] = 'short'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Registration fails when email already exists."""
        User.objects.create_user(email='john@example.com', name='John', password='password123')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Login Tests (SimpleJWT) ---

    def test_login_success(self):
        """User logs in with valid credentials and receives JWT tokens."""
        User.objects.create_user(email='john@example.com', name='John Doe', password='password123')
        credentials = {'email': 'john@example.com', 'password': 'password123'}
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password(self):
        """Login fails when given an incorrect password."""
        User.objects.create_user(email='john@example.com', name='John Doe', password='password123')
        credentials = {'email': 'john@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
