from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.companies.models import CompanyProfile, CarrierCompany

User = get_user_model()

class CompaniesTests(APITestCase):
    """
    Test suite for CompanyProfile and CarrierCompany endpoints.
    Assessing raw responses directly as returned before JSON rendering in DRF testing.
    """
    def setUp(self):
        # Create users
        self.pj_user = User.objects.create_user(
            email="pj@fretehub.com",
            password="Password123",
            name="PJ Client",
            user_type="PJ"
        )
        self.carrier_user = User.objects.create_user(
            email="carrier@fretehub.com",
            password="Password123",
            name="Carrier Driver",
            user_type="CARRIER"
        )
        self.pf_user = User.objects.create_user(
            email="pf@fretehub.com",
            password="Password123",
            name="PF Client",
            user_type="PF"
        )

        self.company_list_url = reverse('company-list')
        self.carrier_list_url = reverse('carrier-list')
        self.company_me_url = reverse('company-me')
        self.carrier_me_url = reverse('carrier-me')

        self.company_payload = {
            "legal_name": "Logistica Ltda",
            "trade_name": "Logi",
            "cnpj": "12.345.678/0001-90",
            "state_registration": "123",
            "responsible_name": "Responsavel",
            "responsible_phone": "11988887777",
            "billing_address": "Rua Faturamento, 10",
            "operational_address": "Rua Operacional, 20"
        }

        self.carrier_payload = {
            "legal_name": "Transportes S/A",
            "trade_name": "Rapido",
            "cnpj": "98.765.432/0001-10",
            "state_registration": "456",
            "responsible_name": "Gerente",
            "responsible_phone": "11955554444",
            "billing_address": "Rua Carrier, 100",
            "operational_address": "Rua Fleet, 200"
        }

    def test_pj_client_can_create_company_profile(self):
        """
        Verify PJ user is allowed to create CompanyProfile, and gets linked automatically.
        """
        self.client.force_authenticate(user=self.pj_user)
        response = self.client.post(self.company_list_url, self.company_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['trade_name'], "Logi")
        self.assertEqual(response.data['cnpj'], "12345678000190")  # Cleaned

        # Verify profile is associated
        profile = CompanyProfile.objects.get(user=self.pj_user)
        self.assertEqual(profile.trade_name, "Logi")

        # Test /api/companies/me/
        response_me = self.client.get(self.company_me_url)
        self.assertEqual(response_me.status_code, status.HTTP_200_OK)
        self.assertEqual(response_me.data['trade_name'], "Logi")

    def test_pf_client_cannot_create_company_profile(self):
        """
        Verify that standard PF users are rejected from creating CompanyProfiles.
        """
        self.client.force_authenticate(user=self.pf_user)
        response = self.client.post(self.company_list_url, self.company_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_carrier_user_can_create_carrier_profile(self):
        """
        Verify Carrier user is allowed to create CarrierCompany, and gets linked automatically.
        """
        self.client.force_authenticate(user=self.carrier_user)
        response = self.client.post(self.carrier_list_url, self.carrier_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['trade_name'], "Rapido")

        # Verify profile is associated
        carrier = CarrierCompany.objects.get(owner_user=self.carrier_user)
        self.assertEqual(carrier.trade_name, "Rapido")

        # Test /api/carriers/me/
        response_me = self.client.get(self.carrier_me_url)
        self.assertEqual(response_me.status_code, status.HTTP_200_OK)
        self.assertEqual(response_me.data['trade_name'], "Rapido")
