from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.support.models import SupportTicket

User = get_user_model()

class SupportTicketAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Alice Support",
            email="alice@fretehub.com",
            phone="11999999994",
            document_type="CPF",
            document_number="44444444444",
            user_type="CLIENT"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_and_close_ticket(self):
        # 1. Create a support ticket
        url = reverse('support-tickets-list')
        data = {
            "category": "atraso",
            "priority": "medium",
            "description": "Carga de mercadorias atrasada na rodovia Dutra.",
            "created_from": "portal"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "open")
        self.assertEqual(response.data["category"], "atraso")
        
        ticket_id = response.data["id"]

        # 2. List support tickets
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # 3. Close support ticket
        close_url = reverse('support-tickets-close-ticket', args=[ticket_id])
        response = self.client.post(close_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "closed")
        self.assertIsNotNone(response.data["closed_at"])
