import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai_assistant.models import AIConversation, AIMessage, AIAction, KnowledgeDocument
from apps.ai_assistant.services import IntentClassifier, RAGService, LLMAdapter, AIOrchestrator
from apps.freight.models import FreightOrder
from apps.support.models import SupportTicket
from apps.accounts.models import UserConsent

User = get_user_model()

class IntentClassifierTestCase(TestCase):
    def test_classify_track_order(self):
        intent, confidence = IntentClassifier.classify("Onde está meu frete?")
        self.assertEqual(intent, 'track_order')
        self.assertGreater(confidence, Decimal("0.50"))

    def test_classify_recommend_vehicle(self):
        intent, confidence = IntentClassifier.classify("Qual o caminhão recomendado para transportar geladeira?")
        self.assertEqual(intent, 'recommend_vehicle')
        self.assertGreater(confidence, Decimal("0.50"))

    def test_classify_open_support_ticket(self):
        intent, confidence = IntentClassifier.classify("Minha carga foi danificada e preciso reclamar com o suporte")
        self.assertEqual(intent, 'open_support_ticket')
        self.assertGreater(confidence, Decimal("0.50"))

    def test_classify_general_query(self):
        intent, confidence = IntentClassifier.classify("Quem descobriu o Brasil?")
        self.assertEqual(intent, 'general_query')

class RAGServiceTestCase(TestCase):
    def setUp(self):
        # Create published articles
        self.doc1 = KnowledgeDocument.objects.create(
            title="Transporte de Geladeira",
            category="veiculos",
            content="Geladeiras devem ser transportadas em caminhao bau na vertical.",
            status="published"
        )
        self.doc2 = KnowledgeDocument.objects.create(
            title="Regulamento de Soja",
            category="graos",
            content="Soja deve ser transportada em graneleira coberta de lona.",
            status="published"
        )

    def test_lexical_search_geladeira(self):
        results = RAGService.search("Qual veículo usar para levar geladeira?")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].title, "Transporte de Geladeira")

    def test_lexical_search_soja(self):
        results = RAGService.search("Como carregar soja?")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].title, "Regulamento de Soja")

class AIOrchestratorTestCase(TestCase):
    def setUp(self):
        # Create users
        self.customer1 = User.objects.create_user(
            name="Joao Embarcador",
            email="joao@fretehub.com",
            phone="11999999991",
            document_type="CPF",
            document_number="11111111111",
            user_type="CLIENT"
        )
        self.customer2 = User.objects.create_user(
            name="Maria Invasora",
            email="maria@fretehub.com",
            phone="11999999992",
            document_type="CPF",
            document_number="22222222222",
            user_type="CLIENT"
        )
        # Create freight order for customer 1
        self.order = FreightOrder.objects.create(
            customer=self.customer1,
            origin_address="Sao Paulo",
            origin_latitude=Decimal("-23.550520"),
            origin_longitude=Decimal("-46.633308"),
            destination_address="Rio de Janeiro",
            destination_latitude=Decimal("-22.906847"),
            destination_longitude=Decimal("-43.172896"),
            cargo_category="eletrodomesticos",
            cargo_description="Uma Geladeira Duplex",
            estimated_weight_kg=Decimal("120.00"),
            estimated_volume_m3=Decimal("1.50"),
            required_vehicle_type="VUC",
            required_body_type="bau",
            estimated_distance_km=Decimal("430.00"),
            estimated_duration_minutes=360,
            estimated_price=Decimal("800.00"),
            final_price=Decimal("800.00")
        )

    def test_track_own_order(self):
        # Customer 1 tries to track their own order
        msg = AIOrchestrator.process_message(
            user=self.customer1,
            message_text=f"onde esta o meu frete {str(self.order.id)}?"
        )
        self.assertEqual(msg.intent, 'track_order')
        self.assertIn("status atualizado", msg.message_text.lower())

    def test_track_unauthorized_order(self):
        # Customer 2 tries to track Customer 1's order
        msg = AIOrchestrator.process_message(
            user=self.customer2,
            message_text=f"onde esta o meu frete {str(self.order.id)}?"
        )
        self.assertIn("questões de segurança e privacidade", msg.message_text)

    def test_automatic_support_ticket_creation(self):
        # Customer 1 reports a damaged cargo
        msg = AIOrchestrator.process_message(
            user=self.customer1,
            message_text="minha carga de geladeira chegou avariada e quebrada"
        )
        self.assertEqual(msg.intent, 'open_support_ticket')
        self.assertIn("Ocorrência Registrada com Sucesso", msg.message_text)
        
        # Verify ticket was created in database
        ticket = SupportTicket.objects.filter(user=self.customer1).first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.category, 'carga_danificada')
        self.assertEqual(ticket.priority, 'high')

class AIAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Pedro Logistico",
            email="pedro@fretehub.com",
            phone="11999999993",
            document_type="CPF",
            document_number="33333333333",
            user_type="CLIENT"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_chat(self):
        url = reverse('ai-chat-api')
        data = {"message_text": "Qual o veículo recomendado para geladeiras?"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message_text", response.data)
        self.assertEqual(response.data["intent"], "recommend_vehicle")

    def test_api_escalate(self):
        conv = AIConversation.objects.create(user=self.user, status='active')
        url = reverse('ai-conversations-escalate', args=[conv.id])
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "escalated")

    def test_api_consent(self):
        url = reverse('user-consent-list')
        data = {
            "consent_type": "privacy_policy",
            "accepted": True,
            "version": "1.0"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["accepted"])
        self.assertEqual(response.data["ip_address"], "127.0.0.1")
