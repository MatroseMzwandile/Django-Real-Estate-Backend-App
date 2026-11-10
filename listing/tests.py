from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Listing

User = get_user_model()


class ListingPermissionAndSearchTests(APITestCase):
    databases = {'default', 'users', 'listings'}

    def setUp(self):
        self.manage_url = '/api/listing/manage'
        self.search_url = '/api/listing/search'

        # Regular (non-realtor) user
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            name='Regular User',
            password='password123',
        )

        # Realtor user
        self.realtor_user = User.objects.create_realtor(
            email='realtor@example.com',
            name='Agent Smith',
            password='password123',
        )

        # Sample listing
        self.listing = Listing.objects.create(
            realtor=self.realtor_user.email,
            title='Sunny Modern Condo in Dallas',
            slug='sunny-modern-condo-dallas',
            address='123 Main St',
            city='Dallas',
            state='TX',
            zipcode='75001',
            description='A beautiful sunny condo in downtown.',
            price=350000,
            bedrooms=2,
            bathrooms=2.0,
            sale_type='For Sale',
            home_type='Condo',
            main_photo='listings/sample.jpg',
            photo_1='listings/sample.jpg',
            photo_2='listings/sample.jpg',
            photo_3='listings/sample.jpg',
            is_published=True,
        )

    # --- Realtor-Only Access Tests ---

    def test_manage_listing_unauthenticated(self):
        """Unauthenticated requests are rejected with 401 Unauthorized."""
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manage_listing_non_realtor_forbidden(self):
        """Logged-in users who are NOT realtors receive 403 Forbidden."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manage_listing_realtor_allowed(self):
        """Realtors can successfully access the manage endpoint."""
        self.client.force_authenticate(user=self.realtor_user)
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('listing', response.data)

    # --- Search and Filter Tests ---

    def test_search_missing_criteria(self):
        """Search returns 400 when missing required search criteria."""
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_invalid_numeric_parameters(self):
        """Search returns 400 when max_price or bedrooms are non-numeric."""
        params = {
            'search': 'Condo',
            'city': 'Dallas',
            'state': 'TX',
            'max_price': 'not-a-number',
            'bedrooms': 2,
            'bathrooms': 2.0,
            'sale_type': 'FOR_SALE',
        }
        response = self.client.get(self.search_url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_no_matching_criteria(self):
        """Search returns 404 when no published listings match criteria."""
        params = {
            'search': 'Skyscraper',
            'city': 'Houston',
            'state': 'TX',
            'max_price': 100000,
            'bedrooms': 5,
            'bathrooms': 4.0,
            'sale_type': 'FOR_RENT',
        }
        response = self.client.get(self.search_url, params)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
