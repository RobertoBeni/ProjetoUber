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
from apps.tracking.models import TrackingEvent
from apps.tracking.services import TrackingService, RedisTrackingClient

User = get_user_model()

class TelemetryAndTrackingTests(APITestCase):
    def setUp(self):
        # 1. Create standard stakeholders
        self.customer = User.objects.create_user(
            email="cliente_test@fretehub.com",
            password="ClientPassword123",
            name="Roberto Cliente",
            phone="(11) 98888-7777",
            document_type="CPF",
            document_number="11122233344",
            user_type="CLIENT",
            is_verified=True
        )
        self.driver_user = User.objects.create_user(
            email="motorista_test@fretehub.com",
            password="DriverPassword123",
            name="Marcos Motorista",
            phone="(11) 97777-6666",
            document_type="CPF",
            document_number="22233344455",
            user_type="DRIVER",
            is_verified=True
        )
        self.other_driver = User.objects.create_user(
            email="outromotorista@fretehub.com",
            password="OtherPassword123",
            name="Outro Motorista",
            phone="(11) 96666-5555",
            document_type="CPF",
            document_number="33344455566",
            user_type="DRIVER",
            is_verified=True
        )
        self.admin_user = User.objects.create_superuser(
            email="admin_test@fretehub.com",
            password="AdminPassword123",
            name="Admin UberLog",
            phone="(11) 99999-9999",
            document_type="CPF",
            document_number="99999999999"
        )

        # 2. Setup Driver profiles
        self.driver_profile = DriverProfile.objects.create(
            user=self.driver_user,
            cnh_number="98765432100",
            cnh_category="AD",
            cnh_expiration_date=datetime.date.today() + datetime.timedelta(days=365),
            status="approved",
            is_online=True,
            rating=Decimal("4.80"),
            accepts_equipment=True,
            current_latitude=Decimal("-23.550520"),
            current_longitude=Decimal("-46.633308")
        )
        self.other_driver_profile = DriverProfile.objects.create(
            user=self.other_driver,
            cnh_number="12345678900",
            cnh_category="B",
            cnh_expiration_date=datetime.date.today() + datetime.timedelta(days=365),
            status="approved",
            is_online=True
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
        self.cargo_type = CargoType.objects.create(
            name="Geladeira",
            category="EQUIPMENTS",
            slug="geladeira",
            is_active=True
        )
        self.rule = CargoRule.objects.create(
            cargo_type=self.cargo_type,
            recommended_vehicle_types=["LIGHT_TRUCK"],
            required_body_types=["BOX"],
            requires_covered_vehicle=True
        )

        # 4. Generate direct Freight Order in transit
        self.order = FreightOrder.objects.create(
            customer=self.customer,
            driver=self.driver_user,
            vehicle=self.vehicle,
            origin_address="Rua Augusta, 100, São Paulo",
            origin_latitude=Decimal("-23.550520"),
            origin_longitude=Decimal("-46.633308"),
            destination_address="Rua Pamplona, 500, São Paulo",
            destination_latitude=Decimal("-23.562000"),
            destination_longitude=Decimal("-46.654000"),
            cargo_category="EQUIPMENTS",
            cargo_description="Geladeira Duplex",
            estimated_weight_kg=Decimal("95.00"),
            estimated_volume_m3=Decimal("1.50"),
            required_vehicle_type="LIGHT_TRUCK",
            required_body_type="BOX",
            estimated_distance_km=Decimal("3.20"),
            estimated_duration_minutes=25,
            estimated_price=Decimal("80.00"),
            final_price=Decimal("80.00"),
            status="in_transit"
        )

        # Create Payment
        self.payment = Payment.objects.create(
            freight_order=self.order,
            payer=self.customer,
            driver=self.driver_user,
            amount=Decimal("80.00"),
            platform_fee=Decimal("12.00"),
            driver_amount=Decimal("68.00"),
            status="paid",
            payment_method="pix"
        )

        # 5. Generate JWT tokens for requests
        response = self.client.post(reverse('auth-login'), {
            "email": "cliente_test@fretehub.com",
            "password": "ClientPassword123"
        }, format='json')
        self.customer_token = response.data['access']

        response = self.client.post(reverse('auth-login'), {
            "email": "motorista_test@fretehub.com",
            "password": "DriverPassword123"
        }, format='json')
        self.driver_token = response.data['access']

        response = self.client.post(reverse('auth-login'), {
            "email": "outromotorista@fretehub.com",
            "password": "OtherPassword123"
        }, format='json')
        self.other_driver_token = response.data['access']

        response = self.client.post(reverse('auth-login'), {
            "email": "admin_test@fretehub.com",
            "password": "AdminPassword123"
        }, format='json')
        self.admin_token = response.data['access']

    def test_driver_submits_telemetry_successfully(self):
        """
        Verify that a correctly assigned driver can submit telemetry coordinates,
        updating Redis, DB, ETA, and driver/vehicle state.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')
        
        payload = {
            "freight_order_id": str(self.order.id),
            "driver_id": str(self.driver_user.id),
            "latitude": "-23.555000",
            "longitude": "-46.640000",
            "speed": "35.50",
            "heading": "120.00"
        }
        
        url = reverse('tracking-location')
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['event_type'], 'location_updated')
        
        # Verify db persistence
        self.assertTrue(TrackingEvent.objects.filter(freight_order=self.order, event_type='location_updated').exists())
        
        # Verify Driver profile coordinate update
        self.driver_profile.refresh_from_db()
        self.assertEqual(self.driver_profile.current_latitude, Decimal("-23.555000"))
        
        # Verify Vehicle coordinate update
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_latitude, Decimal("-23.555000"))

    def test_wrong_driver_blocked_from_sending_telemetry(self):
        """
        Verify that a driver not assigned to the order is prevented from submitting location data.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_driver_token}')
        
        payload = {
            "freight_order_id": str(self.order.id),
            "driver_id": str(self.other_driver.id),
            "latitude": "-23.555000",
            "longitude": "-46.640000",
            "speed": "25.00"
        }
        
        url = reverse('tracking-location')
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])

    def test_automatic_stop_detection(self):
        """
        Verify that transmitting very low speeds over a duration flags a stopped status.
        """
        # Directly execute service methods to simulate time passage
        # Speed = 0.0
        now = timezone.now()
        TrackingService.process_telemetry(
            freight_order_id=self.order.id,
            driver_user=self.driver_user,
            latitude=-23.551000,
            longitude=-46.634000,
            speed=0.00,
            timestamp=now
        )
        
        # Speed = 0.0, 6 minutes later
        future_time = now + datetime.timedelta(minutes=6)
        TrackingService.process_telemetry(
            freight_order_id=self.order.id,
            driver_user=self.driver_user,
            latitude=-23.551000,
            longitude=-46.634000,
            speed=0.00,
            timestamp=future_time
        )
        
        self.order.refresh_from_db()
        # Should change status to temporarily_stopped
        self.assertEqual(self.order.status, 'temporarily_stopped')
        self.assertTrue(TrackingEvent.objects.filter(freight_order=self.order, event_type='stop_detected').exists())

    def test_automatic_route_deviation_detection(self):
        """
        Verify that moving geographically far from origin-destination straight line triggers a deviation.
        """
        # Coordinates way off the route (-23.55, -46.63) -> (-23.56, -46.65)
        # Off coordinate: -23.700000, -46.400000
        TrackingService.process_telemetry(
            freight_order_id=self.order.id,
            driver_user=self.driver_user,
            latitude=-23.700000,
            longitude=-46.400000,
            speed=55.00
        )
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'route_deviation_detected')
        self.assertTrue(TrackingEvent.objects.filter(freight_order=self.order, event_type='route_deviation').exists())

    def test_fetch_tracking_details_and_events_api(self):
        """
        Validate client querying real-time positions and historical event arrays.
        """
        # Create an event in DB
        TrackingEvent.objects.create(
            freight_order=self.order,
            driver=self.driver_user,
            event_type='route_started',
            latitude=self.order.origin_latitude,
            longitude=self.order.origin_longitude,
            description="Motorista iniciou trajeto."
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        
        # Detail position
        url = reverse('freight-tracking-detail', kwargs={'pk': str(self.order.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Events history
        url = reverse('freight-events-list', kwargs={'pk': str(self.order.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_admin_reports_metrics(self):
        """
        Validate administrative KPIs and operational distribution summaries endpoints.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        # KPIs
        url = reverse('api-admin-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['kpis']['total_orders'], 1)
        self.assertEqual(response.data['data']['kpis']['total_revenue'], "80.00")
        
        # Operations
        url = reverse('api-report-operations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('in_transit', response.data['data']['status_distribution'])
        
        # Financial
        url = reverse('api-report-financial')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['platform_earnings'], "12.00")
