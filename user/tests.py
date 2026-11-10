from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterTests(TestCase):
    databases = '__all__'  # the project uses two databases (users and listings)

    def register(self, email, **extra):
        payload = {
            'name': 'Test User',
            'email': email,
            'password': 'password123',
            're_password': 'password123',
        }
        payload.update(extra)
        return APIClient().post('/auth/user/register', payload, format='json')

    def test_signup_cannot_become_realtor(self):
        response = self.register('mallory@example.com', is_realtor='True')

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='mallory@example.com')
        self.assertFalse(user.is_realtor)

    def test_normal_signup_without_is_realtor_still_works(self):
        response = self.register('alice@example.com')

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='alice@example.com')
        self.assertFalse(user.is_realtor)