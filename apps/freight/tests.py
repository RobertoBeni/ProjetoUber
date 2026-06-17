import datetime
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.cargo.models import CargoType, CargoRule
from apps.vehicles.models import Vehicle
from apps.drivers.models import DriverProfile
from apps.freight.models import FreightOrder, CargoItem
from apps.payments.models import Payment
from apps.notifications.models import Notification
from apps.matching.models import MatchCandidate

User = get_user_model()

class LogisticsWorkflowTests(APITestCase):
    def setUp(self):
        # 1. Create standard stakeholders
        self.customer = User.objects.create_user(
            email="cliente@fretehub.com",
            password="ClientPassword123",
            name="Roberto Cliente",
            phone="(11) 98888-7777",
            document_type="CPF",
            document_number="11122233344",
            user_type="CLIENT",
            is_verified=True
        )
        self.driver_user = User.objects.create_user(
            email="motorista@fretehub.com",
            password="DriverPassword123",
            name="Marcos Motorista",
            phone="(11) 97777-6666",
            document_type="CPF",
            document_number="22233344455",
            user_type="DRIVER",
            is_verified=True
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@fretehub.com",
            password="AdminPassword123",
            name="Admin UberLog",
            phone="(11) 99999-9999",
            document_type="CPF",
            document_number="99999999999"
        )

        # 2. Setup Driver profile and approved vehicle
        self.driver_profile = DriverProfile.objects.create(
            user=self.driver_user,
            cnh_number="98765432100",
            cnh_category="AD",
            cnh_expiration_date=datetime.date.today() + datetime.timedelta(days=365),
            status="approved",
            is_online=True,
            rating=Decimal("4.80"),
            accepts_equipment=True,
            accepts_dry_grains=True,
            current_latitude=Decimal("-23.550520"),
            current_longitude=Decimal("-46.633308")
        )
        
        self.vehicle = Vehicle.objects.create(
            owner_driver=self.driver_user,
            plate="ABC-1234",
            renavam="12345678901",
            brand="Mercedes-Benz",
            model="Sprinter",
            year=2021,
            vehicle_type="LIGHT_TRUCK",
            body_type="BOX",
            max_weight_kg=Decimal("3500.00"),
            max_volume_m3=Decimal("15.00"),
            status="approved"
        )

        # 3. Create database Cargo Types & Rules
        self.cargo_type_fridge = CargoType.objects.create(
            name="Geladeira Doméstica",
            category="EQUIPMENTS",
            slug="geladeira",
            is_active=True
        )
        self.rule_fridge = CargoRule.objects.create(
            cargo_type=self.cargo_type_fridge,
            recommended_vehicle_types=["LIGHT_TRUCK", "PICKUP"],
            required_body_types=["BOX"],
            requires_covered_vehicle=True,
            requires_helper_recommended=True,
            requires_insurance_recommended=True,
            handling_instructions="Geladeira deve ser transportada em pé."
        )

        self.cargo_type_soja = CargoType.objects.create(
            name="Soja a Granel",
            category="DRY_GRAINS",
            slug="soja",
            is_active=True
        )
        self.rule_soja = CargoRule.objects.create(
            cargo_type=self.cargo_type_soja,
            recommended_vehicle_types=["GRAIN_TRUCK"],
            required_body_types=["GRAIN"],
            requires_grain_body=True,
            requires_tarp=True,
            requires_invoice=True,
            requires_weighing=True,
            handling_instructions="Cobrir com lona e fazer pesagem na origem e destino."
        )

        # 4. Generate JWT tokens for requests
        response = self.client.post(reverse('auth-login'), {
            "email": "cliente@fretehub.com",
            "password": "ClientPassword123"
        }, format='json')
        self.customer_token = response.data['access']

        response = self.client.post(reverse('auth-login'), {
            "email": "motorista@fretehub.com",
            "password": "DriverPassword123"
        }, format='json')
        self.driver_token = response.data['access']

    def test_complete_logistics_flow_fridge(self):
        """
        Validate creation of a freight solicitation for a household appliance (Fridge),
        clearing payment, executing matching, accepting freight, completing transit stages
        and verifying notifications.
        """
        # --- PHASE 1: Solicitation Creation ---
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        
        payload = {
            "origin_address": "Rua Augusta, 100, São Paulo",
            "origin_latitude": "-23.550520",
            "origin_longitude": "-46.633308",
            "destination_address": "Rua Pamplona, 500, São Paulo",
            "destination_latitude": "-23.562000",
            "destination_longitude": "-46.654000",
            "cargo_category": "EQUIPMENTS",
            "cargo_description": "Mudança residencial de geladeira",
            "items": [
                {
                    "cargo_type_slug": "geladeira",
                    "description": "Geladeira Duplex Continental",
                    "estimated_weight_kg": 95.0,
                    "estimated_volume_m3": 1.5,
                    "quantity": 1,
                    "is_fragile": True
                }
            ]
        }
        
        create_url = reverse('freight-order-list')
        response = self.client.post(create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        order_id = response.data['id']
        self.assertEqual(response.data['status'], 'requested')
        self.assertEqual(response.data['required_vehicle_type'], 'LIGHT_TRUCK')
        self.assertTrue(response.data['requires_helper'])
        self.assertTrue(response.data['requires_insurance'])
        self.assertGreater(float(response.data['estimated_price']), 0)
        
        # Verify related objects exist
        order = FreightOrder.objects.get(id=order_id)
        self.assertIsNotNone(order.route_details)
        self.assertEqual(order.eta_records.count(), 1)
        
        payment = Payment.objects.get(freight_order=order)
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.amount, order.estimated_price)
        
        # Verify requested notification
        self.assertTrue(Notification.objects.filter(user=self.customer, notification_type='freight_requested').exists())

        # --- PHASE 2: Payment Confirmation & Match Scoring ---
        # Simulate customer payment confirmation
        pay_url = reverse('payment-simulate-confirmation', kwargs={'pk': str(payment.id)})
        response = self.client.post(pay_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'paid')
        
        # Verify freight order advanced to waiting_driver
        order.refresh_from_db()
        self.assertEqual(order.status, 'waiting_driver')
        
        # Verify payment confirmed notification
        self.assertTrue(Notification.objects.filter(user=self.customer, notification_type='PAYMENT_CONFIRMED').exists())

        # Verify matching candidates exist and are ranked
        match_url = reverse('freight-order-run-matching', kwargs={'pk': str(order.id)})
        response = self.client.post(match_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(str(response.data[0]['driver']), str(self.driver_user.id))

        # --- PHASE 3: Driver Acceptance ---
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        
        accept_url = reverse('freight-order-accept', kwargs={'pk': str(order.id)})
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'driver_found')
        self.assertEqual(str(response.data['driver']), str(self.driver_user.id))
        self.assertEqual(str(response.data['vehicle']), str(self.vehicle.id))
        
        # Verify customer notification that driver accepted
        self.assertTrue(Notification.objects.filter(user=self.customer, notification_type='driver_accepted').exists())

        # --- PHASE 4: Logistics Tracking Execution ---
        # 1. Driver arrived at origin
        arrived_url = reverse('freight-order-arrived-origin', kwargs={'pk': str(order.id)})
        response = self.client.post(arrived_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'arrived_at_origin')
        self.assertTrue(Notification.objects.filter(user=self.customer, notification_type='arrived_origin').exists())

        # 2. Driver collects cargo
        collect_url = reverse('freight-order-collect', kwargs={'pk': str(order.id)})
        response = self.client.post(collect_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cargo_collected')
        self.assertTrue(Notification.objects.filter(user=self.customer, notification_type='cargo_collected').exists())

        # 3. Driver starts transit
        transit_url = reverse('freight-order-start-transit', kwargs={'pk': str(order.id)})
        response = self.client.post(transit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_transit')
        self.assertTrue(Notification.objects.filter(user=self.customer, notification_type='in_transit').exists())
        
        # Verify ETA record has been updated / appended
        self.assertEqual(order.eta_records.count(), 2)

        # 4. Driver arrived at destination
        dest_url = reverse('freight-order-arrived-destination', kwargs={'pk': str(order.id)})
        response = self.client.post(dest_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'arrived_at_destination')

        # 5. Driver delivers cargo
        deliver_url = reverse('freight-order-deliver', kwargs={'pk': str(order.id)})
        response = self.client.post(deliver_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'delivered')
        self.assertTrue(Notification.objects.filter(user=self.customer, notification_type='delivered').exists())

        # --- PHASE 5: Completion ---
        # Customer completes freight order
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        complete_url = reverse('freight-order-complete', kwargs={'pk': str(order.id)})
        response = self.client.post(complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        
        # Verify driver is notified of completion
        self.assertTrue(Notification.objects.filter(user=self.driver_user, title="Frete Concluído").exists())

    def test_customer_cancellation_voids_payment(self):
        """
        Verify that cancelling a requested freight order voids any linked pending payment.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        
        payload = {
            "origin_address": "Rua Augusta, 100, São Paulo",
            "origin_latitude": "-23.550520",
            "origin_longitude": "-46.633308",
            "destination_address": "Rua Pamplona, 500, São Paulo",
            "destination_latitude": "-23.562000",
            "destination_longitude": "-46.654000",
            "cargo_category": "EQUIPMENTS",
            "cargo_description": "Mudança residencial de geladeira",
            "items": [
                {
                    "cargo_type_slug": "geladeira",
                    "description": "Geladeira Duplex Continental",
                    "estimated_weight_kg": 95.0,
                    "estimated_volume_m3": 1.5,
                    "quantity": 1,
                    "is_fragile": True
                }
            ]
        }
        
        create_res = self.client.post(reverse('freight-order-list'), payload, format='json')
        order_id = create_res.data['id']
        
        # Void/Cancel
        cancel_url = reverse('freight-order-cancel', kwargs={'pk': order_id})
        response = self.client.post(cancel_url, {"cancellation_reason": "Desisti do envio"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')
        
        # Check payment record is cancelled
        payment = Payment.objects.get(freight_order_id=order_id)
        self.assertEqual(payment.status, 'cancelled')
