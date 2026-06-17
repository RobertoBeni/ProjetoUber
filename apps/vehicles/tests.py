import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.vehicles.models import Vehicle

User = get_user_model()

class VehicleTests(APITestCase):
    def setUp(self):
        self.driver_user = User.objects.create_user(
            email="driver_veh@fretehub.com",
            password="DriverPassword123",
            name="Carlos Driver",
            phone="(11) 96666-4444",
            document_type="CPF",
            document_number="44444444444",
            user_type="DRIVER",
            is_verified=True
        )
        self.other_driver = User.objects.create_user(
            email="other_driver@fretehub.com",
            password="DriverPassword123",
            name="Other Driver",
            phone="(11) 95555-5555",
            document_type="CPF",
            document_number="55555555555",
            user_type="DRIVER",
            is_verified=True
        )
        self.admin_user = User.objects.create_superuser(
            email="admin_veh@fretehub.com",
            password="AdminPassword123",
            name="Admin User",
            phone="(11) 99999-1111",
            document_type="CPF",
            document_number="11111111111"
        )

        # Login driver and setup tokens
        response = self.client.post(reverse('auth-login'), {
            "email": "driver_veh@fretehub.com",
            "password": "DriverPassword123"
        }, format='json')
        self.driver_token = response.data['access']

        # Login other driver
        response = self.client.post(reverse('auth-login'), {
            "email": "other_driver@fretehub.com",
            "password": "DriverPassword123"
        }, format='json')
        self.other_driver_token = response.data['access']

        # Login admin
        response = self.client.post(reverse('auth-login'), {
            "email": "admin_veh@fretehub.com",
            "password": "AdminPassword123"
        }, format='json')
        self.admin_token = response.data['access']

        self.vehicle_payload = {
            "plate": "ABC-9999",
            "renavam": "12345678901",
            "brand": "Volvo",
            "model": "FH 540",
            "year": 2020,
            "vehicle_type": "GRAIN_TRUCK",
            "body_type": "GRAIN",
            "max_weight_kg": 14000.00,
            "max_volume_m3": 45.00,
            "allowed_cargo_types": ["soja"],
            "has_insurance": True,
            "insurance_policy_number": "INS-111"
        }

    def test_vehicle_creation_and_ownership(self):
        """Verify vehicle creation works and sets status to pending."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        response = self.client.post(reverse('vehicle-list'), self.vehicle_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['owner_driver'], self.driver_user.id)

    def test_vehicle_age_validation(self):
        """Verify vehicle validation rule rejecting vehicles older than 40 years."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        invalid_payload = self.vehicle_payload.copy()
        invalid_payload['year'] = datetime.date.today().year - 45  # 45 years old
        response = self.client.post(reverse('vehicle-list'), invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("40 anos", response.data['year'][0])

    def test_vehicle_access_authorization_boundaries(self):
        """Verify driver cannot see or submit review for other driver's vehicles."""
        # 1. Driver 1 creates a vehicle
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        res = self.client.post(reverse('vehicle-list'), self.vehicle_payload, format='json')
        vehicle_id = res.data['id']

        # 2. Driver 2 lists vehicles - should be empty for them
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_driver_token}')
        list_res = self.client.get(reverse('vehicle-list'))
        self.assertEqual(len(list_res.data), 0)

        # 3. Driver 2 tries to submit review for Driver 1's vehicle - should be forbidden
        review_submit_url = reverse('vehicle-submit-review', kwargs={'pk': vehicle_id})
        response = self.client.post(review_submit_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_review_vehicle(self):
        """Verify admin can review and approve a vehicle."""
        # 1. Create vehicle
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        res = self.client.post(reverse('vehicle-list'), self.vehicle_payload, format='json')
        vehicle_id = res.data['id']

        # 2. Review as Admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        review_url = reverse('admin-vehicle-review', kwargs={'pk': vehicle_id})
        response = self.client.patch(review_url, {"status": "approved"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'approved')
