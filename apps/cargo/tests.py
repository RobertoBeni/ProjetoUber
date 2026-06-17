from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.cargo.models import CargoType, CargoRule

User = get_user_model()

class CargoCompatibilityTests(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email="cargo_test@fretehub.com",
            password="Password123",
            name="Cargo Tester",
            phone="(11) 98888-7777",
            document_type="CPF",
            document_number="12345678901",
            user_type="PF",
            is_verified=True
        )
        
        # Login
        response = self.client.post(reverse('auth-login'), {
            "email": "cargo_test@fretehub.com",
            "password": "Password123"
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Setup CargoTypes and CargoRules
        self.geladeira = CargoType.objects.create(
            name="Geladeira",
            category="EQUIPMENTS",
            slug="geladeira",
            is_active=True
        )
        self.geladeira_rule = CargoRule.objects.create(
            cargo_type=self.geladeira,
            recommended_vehicle_types=["SMALL_UTILITY", "PICKUP", "VAN"],
            required_body_types=["BOX", "SIDER"],
            requires_covered_vehicle=True,
            requires_helper_recommended=True,
            handling_instructions="Transportar em pé."
        )

        self.soja = CargoType.objects.create(
            name="Soja",
            category="DRY_GRAINS",
            slug="soja",
            is_active=True
        )
        self.soja_rule = CargoRule.objects.create(
            cargo_type=self.soja,
            recommended_vehicle_types=["GRAIN_TRUCK", "GRAIN_TRAILER"],
            required_body_types=["GRAIN"],
            requires_grain_body=True,
            requires_tarp=True,
            requires_invoice=True,
            requires_weighing=True,
            handling_instructions="Exige lona e pesagem."
        )

    def test_list_cargo_types(self):
        """Verify list of active cargo types is returned."""
        url = reverse('cargo-type-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify geladeira and soja are in list
        slugs = [item['slug'] for item in response.data]
        self.assertIn('geladeira', slugs)
        self.assertIn('soja', slugs)

    def test_recommendation_geladeira(self):
        """Verify logistical heuristics for geladeira."""
        url = reverse('cargo-type-recommend-vehicle')
        payload = {
            "cargo_type": "geladeira",
            "weight_kg": 75,
            "volume_m3": 1.8,
            "quantity": 1,
            "is_fragile": True
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify recommended types and warnings
        self.assertIn("SMALL_UTILITY", response.data['recommended_vehicle_types'])
        self.assertIn("BOX", response.data['required_body_types'])
        self.assertTrue(any("em pé" in w for w in response.data['warnings']))
        self.assertTrue(response.data['requires_helper'])
        self.assertTrue(response.data['requires_insurance'])

    def test_recommendation_dry_grains(self):
        """Verify logistical heuristics for dry grains."""
        url = reverse('cargo-type-recommend-vehicle')
        payload = {
            "cargo_type": "soja",
            "weight_kg": 12000,
            "volume_m3": 30,
            "quantity": 1,
            "is_fragile": False
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify rules
        self.assertIn("GRAIN_TRUCK", response.data['recommended_vehicle_types'])
        self.assertIn("GRAIN", response.data['required_body_types'])
        self.assertTrue(response.data['requires_invoice'])
        self.assertTrue(response.data['requires_weighing'])
        self.assertTrue(any("agrícola" in w for w in response.data['warnings']))

    def test_recommendation_fallback(self):
        """Verify operational fallback rules are applied when slug is invalid."""
        url = reverse('cargo-type-recommend-vehicle')
        payload = {
            "cargo_type": "slug_inexistente",
            "weight_kg": 10,
            "volume_m3": 0.5
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("PICKUP", response.data['recommended_vehicle_types'])
        self.assertTrue(any("padrão" in w for w in response.data['warnings']))
