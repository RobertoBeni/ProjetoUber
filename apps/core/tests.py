from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.conf import settings

User = get_user_model()

class CoreAPITests(APITestCase):
    def setUp(self):
        self.normal_user = User.objects.create_user(
            email="normal_client@fretehub.com",
            password="ClientPassword123",
            name="Roberto Cliente",
            user_type="PF"
        )
        
        self.admin_user = User.objects.create_user(
            email="admin_metrics@fretehub.com",
            password="AdminPassword123",
            name="Admin Relatorios",
            user_type="ADMIN"
        )

    def test_public_freight_simulator(self):
        url = reverse('api-public-freight-simulator')
        payload = {
            "origin_latitude": -15.596,
            "origin_longitude": -56.096,
            "destination_latitude": -15.650,
            "destination_longitude": -56.130,
            "weight_kg": 250,
            "volume_m3": 1.8,
            "cargo_category": "equipamentos",
            "requires_helper": True,
            "requires_insurance": True
        }
        
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        
        data = response.data["data"]
        self.assertIn("distance_km", data)
        self.assertIn("recommended_vehicle", data)
        self.assertIn("pricing", data)
        
        pricing = data["pricing"]
        self.assertEqual(pricing["helper_fee"], "100.00")
        self.assertEqual(pricing["insurance_fee"], "35.00")
        self.assertIsNotNone(pricing["total_estimated_price"])

    def test_metrics_endpoints_restrictions(self):
        # Public cannot view metrics
        url_exec = reverse('api-metrics-executive')
        response_pub = self.client.get(url_exec)
        self.assertEqual(response_pub.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Normal client cannot view metrics
        self.client.force_authenticate(user=self.normal_user)
        response_norm = self.client.get(url_exec)
        self.assertEqual(response_norm.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin staff can view metrics
        self.client.force_authenticate(user=self.admin_user)
        response_admin = self.client.get(url_exec)
        self.assertEqual(response_admin.status_code, status.HTTP_200_OK)
        self.assertTrue(response_admin.data["success"])
        self.assertIn("total_gmv", response_admin.data["data"])
