import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.drivers.models import DriverProfile

User = get_user_model()

class DriverProfileTests(APITestCase):
    def setUp(self):
        # Create users
        self.driver_user = User.objects.create_user(
            email="driver_test@fretehub.com",
            password="DriverPassword123",
            name="Carlos Driver",
            phone="(11) 96666-4444",
            document_type="CPF",
            document_number="44444444444",
            user_type="DRIVER",
            is_verified=True
        )
        self.admin_user = User.objects.create_superuser(
            email="admin_test@fretehub.com",
            password="AdminPassword123",
            name="Admin User",
            phone="(11) 99999-1111",
            document_type="CPF",
            document_number="11111111111"
        )
        
        # Profile creation payload
        self.profile_payload = {
            "cnh_number": "12345678900",
            "cnh_category": "AD",
            "cnh_expiration_date": str(datetime.date.today() + datetime.timedelta(days=365)),
            "pix_key": "12345678900"
        }
        
        # Login driver and setup tokens
        response = self.client.post(reverse('auth-login'), {
            "email": "driver_test@fretehub.com",
            "password": "DriverPassword123"
        }, format='json')
        self.driver_token = response.data['access']

        # Login admin
        response = self.client.post(reverse('auth-login'), {
            "email": "admin_test@fretehub.com",
            "password": "AdminPassword123"
        }, format='json')
        self.admin_token = response.data['access']

    def test_driver_profile_creation_and_me(self):
        """Verify driver can create profile and access me endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        
        # Create Profile
        create_url = reverse('driver-list')
        response = self.client.post(create_url, self.profile_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['cnh_number'], "12345678900")
        
        # Retrieve 'me' profile
        me_url = reverse('driver-me')
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cnh_number'], "12345678900")

    def test_driver_go_online_and_offline(self):
        """Verify driver can switch states online/offline."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        
        # Create profile
        self.client.post(reverse('driver-list'), self.profile_payload, format='json')
        
        # Go Online
        online_url = reverse('driver-go-online')
        response = self.client.post(online_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']['is_online'])

        # Go Offline
        offline_url = reverse('driver-go-offline')
        response = self.client.post(offline_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['data']['is_online'])

    def test_driver_go_online_fails_with_expired_cnh(self):
        """Verify driver cannot go online if CNH is expired."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        
        # Directly create profile with expired date in database to bypass serializer validation
        DriverProfile.objects.create(
            user=self.driver_user,
            cnh_number="12345678900",
            cnh_category="AD",
            cnh_expiration_date=datetime.date.today() - datetime.timedelta(days=1),
            status="approved"
        )
        
        online_url = reverse('driver-go-online')
        response = self.client.post(online_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CNH vencida", response.data['detail'])

    def test_admin_review_driver(self):
        """Verify administrative review transitions status."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        create_res = self.client.post(reverse('driver-list'), self.profile_payload, format='json')
        profile_id = create_res.data['id']

        # Review as Admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        review_url = reverse('admin-driver-review', kwargs={'pk': profile_id})
        response = self.client.patch(review_url, {"status": "approved"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'approved')
