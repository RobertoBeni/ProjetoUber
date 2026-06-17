from decimal import Decimal
from django.utils import timezone
from apps.freight.models import FreightOrder, CargoItem
from apps.cargo.models import CargoType
from apps.cargo.services import CargoCompatibilityService
from apps.routing.services import RoutingService
from apps.pricing.services import PricingService
from apps.eta.services import ETAService
from apps.payments.services import PaymentService
from apps.notifications.services import NotificationService
from apps.vehicles.models import Vehicle

class FreightService:
    """
    Central service for orchestration of the freight order lifecycle, cargo analysis,
    vehicle matching compatibility, routing estimations, dynamic pricing, and virtual billing.
    """
    @staticmethod
    def create_freight_order(customer, origin_address, origin_latitude, origin_longitude,
                             destination_address, destination_latitude, destination_longitude, cargo_category,
                             cargo_description, items_data, scheduled_pickup_at=None):
        
        # 1. Sum up cargo metrics across items
        total_weight = Decimal("0.00")
        total_volume = Decimal("0.00")
        requires_helper = False
        requires_insurance = False
        is_fragile = False
        
        for item in items_data:
            qty = int(item.get('quantity', 1))
            total_weight += Decimal(str(item.get('estimated_weight_kg', 0))) * qty
            total_volume += Decimal(str(item.get('estimated_volume_m3', 0))) * qty
            if item.get('requires_helper'):
                requires_helper = True
            if item.get('requires_insurance'):
                requires_insurance = True
            if item.get('is_fragile'):
                is_fragile = True

        # 2. Query vehicle compatibility recommendation
        cargo_type_slug = items_data[0].get('cargo_type_slug') if items_data else None
        recommendation = CargoCompatibilityService.get_recommendation(
            cargo_slug=cargo_type_slug,
            weight_kg=total_weight,
            volume_m3=total_volume,
            quantity=len(items_data),
            is_fragile=is_fragile
        )
        
        # Override or default requirements from recommendation
        required_vehicle_type = recommendation['recommended_vehicle_types'][0] if recommendation['recommended_vehicle_types'] else "PICKUP"
        required_body_type = recommendation['required_body_types'][0] if recommendation['required_body_types'] else "BOX"
        requires_helper = requires_helper or recommendation['requires_helper']
        requires_insurance = requires_insurance or recommendation['requires_insurance']

        # 3. Simulated routing calculation
        route_data = RoutingService.calculate_simulated_route(
            origin_latitude, origin_longitude,
            destination_latitude, destination_longitude
        )
        estimated_distance_km = Decimal(str(route_data['distance_km']))
        estimated_duration_minutes = route_data['duration_minutes']

        # 4. Dynamic price estimation
        price_estimate = PricingService.calculate_estimate(
            customer=customer,
            origin_lat=origin_latitude,
            origin_lng=origin_longitude,
            dest_lat=destination_latitude,
            dest_lng=destination_longitude,
            cargo_type_slug=cargo_type_slug,
            requires_helper=requires_helper,
            requires_insurance=requires_insurance
        )
        estimated_price = price_estimate.total_estimated_price
        final_price = estimated_price

        # 5. Create core FreightOrder record
        freight_order = FreightOrder.objects.create(
            customer=customer,
            origin_address=origin_address,
            origin_latitude=origin_latitude,
            origin_longitude=origin_longitude,
            destination_address=destination_address,
            destination_latitude=destination_latitude,
            destination_longitude=destination_longitude,
            cargo_category=cargo_category,
            cargo_description=cargo_description,
            estimated_weight_kg=total_weight,
            estimated_volume_m3=total_volume,
            required_vehicle_type=required_vehicle_type,
            required_body_type=required_body_type,
            requires_helper=requires_helper,
            requires_insurance=requires_insurance,
            scheduled_pickup_at=scheduled_pickup_at,
            estimated_distance_km=estimated_distance_km,
            estimated_duration_minutes=estimated_duration_minutes,
            estimated_price=estimated_price,
            final_price=final_price,
            status='requested'
        )

        # 6. Instantiate CargoItems
        for item in items_data:
            cargo_type = None
            slug = item.get('cargo_type_slug')
            if slug:
                try:
                    cargo_type = CargoType.objects.get(slug=slug, is_active=True)
                except CargoType.DoesNotExist:
                    pass
                    
            CargoItem.objects.create(
                freight_order=freight_order,
                cargo_type=cargo_type,
                description=item.get('description', ''),
                estimated_weight_kg=Decimal(str(item.get('estimated_weight_kg', 0))),
                estimated_volume_m3=Decimal(str(item.get('estimated_volume_m3', 0))),
                quantity=item.get('quantity', 1),
                is_fragile=item.get('is_fragile', False),
                requires_helper=item.get('requires_helper', False),
                requires_insurance=item.get('requires_insurance', False),
                requires_covered_vehicle=item.get('requires_covered_vehicle', False),
                requires_grain_body=item.get('requires_grain_body', False),
                notes=item.get('notes', '')
            )

        # 7. Generate Route details record
        RoutingService.create_route_for_order(freight_order)

        # 8. Generate dynamic initial ETA record
        ETAService.calculate_and_update_eta(freight_order, reason="inicialização")

        # 9. Link pending virtual Payment
        PaymentService.create_payment_for_order(freight_order)

        # 10. Send client notification
        NotificationService.send_notification(
            user=customer,
            title="Frete Solicitado",
            message=f"Seu pedido de frete {str(freight_order.id)[:8]} foi solicitado com sucesso. Aguardando confirmação de pagamento.",
            notification_type="freight_requested",
            metadata={"freight_order_id": str(freight_order.id)}
        )

        return freight_order

    @staticmethod
    def accept_order(freight_order, driver):
        """
        Accepts the freight order for the given driver. Assigns the driver's approved vehicle.
        """
        # A driver must have an approved vehicle to accept the freight order
        vehicle = Vehicle.objects.filter(owner_driver=driver, status='approved').first()
        if not vehicle:
            raise ValueError("O motorista precisa ter um veículo aprovado no sistema para aceitar fretes.")

        # Update MatchCandidate status
        from apps.matching.models import MatchCandidate
        MatchCandidate.objects.filter(freight_order=freight_order, driver=driver, status='pending').update(status='accepted')
        # Mark other pending ones for this order as expired
        MatchCandidate.objects.filter(freight_order=freight_order, status='pending').exclude(driver=driver).update(status='expired')

        # Update FreightOrder details
        freight_order.driver = driver
        freight_order.vehicle = vehicle
        freight_order.status = 'driver_found'
        freight_order.accepted_at = timezone.now()
        freight_order.save(update_fields=['driver', 'vehicle', 'status', 'accepted_at'])

        # Notify Customer
        NotificationService.send_notification(
            user=freight_order.customer,
            title="Motorista Encontrado",
            message=f"O motorista {driver.name} aceitou seu frete {str(freight_order.id)[:8]} e está a caminho.",
            notification_type="driver_accepted",
            metadata={"freight_order_id": str(freight_order.id), "driver_name": driver.name}
        )

        return freight_order

    @staticmethod
    def arrived_origin(freight_order):
        freight_order.status = 'arrived_at_origin'
        freight_order.save(update_fields=['status'])
        
        # Notify Customer
        NotificationService.send_notification(
            user=freight_order.customer,
            title="Motorista na Origem",
            message=f"O motorista chegou ao endereço de coleta do frete {str(freight_order.id)[:8]}.",
            notification_type="arrived_origin",
            metadata={"freight_order_id": str(freight_order.id)}
        )
        return freight_order

    @staticmethod
    def collect_cargo(freight_order):
        freight_order.status = 'cargo_collected'
        freight_order.picked_up_at = timezone.now()
        freight_order.save(update_fields=['status', 'picked_up_at'])
        
        # Notify Customer
        NotificationService.send_notification(
            user=freight_order.customer,
            title="Carga Coletada",
            message=f"Sua carga foi coletada e está pronta para o trânsito do frete {str(freight_order.id)[:8]}.",
            notification_type="cargo_collected",
            metadata={"freight_order_id": str(freight_order.id)}
        )
        return freight_order

    @staticmethod
    def start_transit(freight_order):
        freight_order.status = 'in_transit'
        freight_order.save(update_fields=['status'])
        
        # Update dynamic ETA dynamically when starting transit!
        ETAService.calculate_and_update_eta(freight_order, reason="início do trânsito")
        
        # Notify Customer
        NotificationService.send_notification(
            user=freight_order.customer,
            title="Frete em Trânsito",
            message=f"Seu frete {str(freight_order.id)[:8]} está em trânsito rumo ao destino.",
            notification_type="in_transit",
            metadata={"freight_order_id": str(freight_order.id)}
        )
        return freight_order

    @staticmethod
    def arrived_destination(freight_order):
        freight_order.status = 'arrived_at_destination'
        freight_order.save(update_fields=['status'])
        
        # Notify Customer
        NotificationService.send_notification(
            user=freight_order.customer,
            title="Motorista no Destino",
            message=f"O motorista chegou ao endereço de destino do frete {str(freight_order.id)[:8]}.",
            notification_type="alert",
            metadata={"freight_order_id": str(freight_order.id)}
        )
        return freight_order

    @staticmethod
    def deliver_cargo(freight_order):
        freight_order.status = 'delivered'
        freight_order.delivered_at = timezone.now()
        freight_order.save(update_fields=['status', 'delivered_at'])
        
        # Notify Customer
        NotificationService.send_notification(
            user=freight_order.customer,
            title="Carga Entregue",
            message=f"O motorista entregou a carga do frete {str(freight_order.id)[:8]}. Por favor, confirme o recebimento.",
            notification_type="delivered",
            metadata={"freight_order_id": str(freight_order.id)}
        )
        return freight_order

    @staticmethod
    def complete_order(freight_order):
        freight_order.status = 'completed'
        freight_order.save(update_fields=['status'])
        
        # Notify Driver (Payment repass simulation or success notification)
        if freight_order.driver:
            NotificationService.send_notification(
                user=freight_order.driver,
                title="Frete Concluído",
                message=f"O frete {str(freight_order.id)[:8]} foi finalizado e o saldo foi liberado em sua carteira.",
                notification_type="alert",
                metadata={"freight_order_id": str(freight_order.id)}
            )
        return freight_order

    @staticmethod
    def cancel_order(freight_order, reason=""):
        freight_order.status = 'cancelled'
        freight_order.cancelled_at = timezone.now()
        freight_order.cancellation_reason = reason
        freight_order.save(update_fields=['status', 'cancelled_at', 'cancellation_reason'])
        
        # Cancel Payment if pending
        from apps.payments.models import Payment
        Payment.objects.filter(freight_order=freight_order, status='pending').update(status='cancelled')
        
        # Notify relevant stakeholders
        NotificationService.send_notification(
            user=freight_order.customer,
            title="Frete Cancelado",
            message=f"O frete {str(freight_order.id)[:8]} foi cancelado. Motivo: {reason}",
            notification_type="alert",
            metadata={"freight_order_id": str(freight_order.id)}
        )
        if freight_order.driver:
            NotificationService.send_notification(
                user=freight_order.driver,
                title="Frete Cancelado pelo Cliente",
                message=f"O frete {str(freight_order.id)[:8]} que você aceitou foi cancelado pelo cliente.",
                notification_type="alert",
                metadata={"freight_order_id": str(freight_order.id)}
            )
        return freight_order
