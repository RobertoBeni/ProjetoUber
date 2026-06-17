import json
import datetime
import math
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from apps.tracking.models import TrackingEvent
from apps.freight.models import FreightOrder
from apps.drivers.models import DriverProfile
from apps.vehicles.models import Vehicle
from apps.eta.services import ETAService
from apps.notifications.services import NotificationService
from apps.routing.services import RoutingService
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import redis

class RedisTrackingClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            try:
                cls._client = redis.from_url(redis_url, decode_responses=True)
                cls._client.ping()
            except Exception:
                # Fallback mock for local development without active Redis service
                class LocalMockRedis:
                    def __init__(self):
                        self.store = {}
                    def set(self, key, value, ex=None):
                        self.store[key] = str(value)
                        return True
                    def get(self, key):
                        return self.store.get(key)
                    def delete(self, *keys):
                        for k in keys:
                            self.store.pop(k, None)
                        return True
                    def ping(self):
                        return True
                cls._client = LocalMockRedis()
        return cls._client

class TrackingService:
    """
    Orchestration service for freight order real-time telemetry, Redis location caching,
    automated stop & route deviation detection, dynamic ETA updates, and Channel broadcasts.
    """
    @staticmethod
    def process_telemetry(freight_order_id, driver_user, latitude, longitude, speed=0.00, heading=0.00, timestamp=None):
        # 1. Fetch and validate FreightOrder
        try:
            freight_order = FreightOrder.objects.get(id=freight_order_id)
        except FreightOrder.DoesNotExist:
            raise ValueError("Ordem de frete não encontrada.")

        # Validate if this driver is assigned to this freight order
        if freight_order.driver != driver_user:
            raise PermissionError("Este motorista não está atribuído a esta ordem de frete.")

        # Ensure active transit state
        if freight_order.status not in ['driver_found', 'driver_going_to_pickup', 'arrived_at_origin', 'cargo_collected', 'in_transit', 'temporarily_stopped', 'route_deviation_detected', 'near_destination', 'arrived_at_destination']:
            raise ValueError(f"Ordem de frete em estado inválido para receber telemetria: {freight_order.status}")

        if timestamp is None:
            timestamp = timezone.now()

        lat_dec = Decimal(str(latitude))
        lng_dec = Decimal(str(longitude))
        speed_dec = Decimal(str(speed))
        heading_dec = Decimal(str(heading))

        # 2. Update Driver and Vehicle geographical positions
        DriverProfile.objects.filter(user=driver_user).update(
            current_latitude=lat_dec,
            current_longitude=lng_dec
        )
        if freight_order.vehicle:
            Vehicle.objects.filter(id=freight_order.vehicle.id).update(
                current_latitude=lat_dec,
                current_longitude=lng_dec
            )

        # 3. Store real-time coordinate state in Redis
        r = RedisTrackingClient.get_client()
        location_data = {
            'latitude': str(lat_dec),
            'longitude': str(lng_dec),
            'speed': str(speed_dec),
            'heading': str(heading_dec),
            'timestamp': timestamp.isoformat(),
            'freight_order_id': str(freight_order.id),
            'driver_id': str(driver_user.id),
            'vehicle_id': str(freight_order.vehicle.id) if freight_order.vehicle else ""
        }
        
        r.set(f"tracking:order:{freight_order.id}:current_location", json.dumps(location_data))
        r.set(f"tracking:driver:{driver_user.id}:current_location", json.dumps(location_data))
        if freight_order.vehicle:
            r.set(f"tracking:vehicle:{freight_order.vehicle.id}:current_location", json.dumps(location_data))

        # 4. Create standard TrackingEvent in database
        previous_status = freight_order.status
        new_status = previous_status  # default
        
        # Calculate remaining distance and check ETA
        remaining_distance = RoutingService.haversine_distance(
            lat_dec, lng_dec,
            freight_order.destination_latitude, freight_order.destination_longitude
        )
        
        # If very close to destination (less than 500 meters), we can update status to arrived_at_destination
        # except if already delivered or completed.
        if remaining_distance < Decimal("0.50") and freight_order.status == 'in_transit':
            new_status = 'near_destination'
            freight_order.status = 'near_destination'
            freight_order.save(update_fields=['status'])

        # Recalculate ETA record
        eta_record = ETAService.calculate_and_update_eta(
            freight_order,
            remaining_distance_km=remaining_distance,
            reason="atualização de telemetria"
        )
        eta_str = freight_order.estimated_arrival_time.isoformat() if freight_order.estimated_arrival_time else ""

        # 5. Smart Stop Detection
        # STOP_DETECTION_MINUTES defaults to 5 minutes
        stop_minutes_limit = getattr(settings, 'STOP_DETECTION_MINUTES', 5)
        
        if speed_dec < Decimal("2.00"):
            # Driver might be stopped
            last_moving_str = r.get(f"tracking:order:{freight_order.id}:last_moving_time")
            if not last_moving_str:
                r.set(f"tracking:order:{freight_order.id}:last_moving_time", timestamp.isoformat())
            else:
                last_moving = timezone.datetime.fromisoformat(last_moving_str)
                delta_minutes = (timestamp - last_moving).total_seconds() / 60.0
                
                # Check if we should flag stopped status
                stop_notified = r.get(f"tracking:order:{freight_order.id}:stop_notified")
                if delta_minutes >= stop_minutes_limit and not stop_notified and freight_order.status == 'in_transit':
                    new_status = 'temporarily_stopped'
                    freight_order.status = 'temporarily_stopped'
                    freight_order.save(update_fields=['status'])
                    
                    r.set(f"tracking:order:{freight_order.id}:stop_notified", "1")
                    
                    # Create Stop Detected Event
                    TrackingEvent.objects.create(
                        freight_order=freight_order,
                        driver=driver_user,
                        vehicle=freight_order.vehicle,
                        event_type='stop_detected',
                        latitude=lat_dec,
                        longitude=lng_dec,
                        speed=speed_dec,
                        heading=heading_dec,
                        description=f"Veículo parado por mais de {stop_minutes_limit} minutos em trânsito.",
                        previous_status=previous_status,
                        new_status=new_status,
                        created_by=driver_user
                    )
                    
                    # Notify Customer
                    NotificationService.send_notification(
                        user=freight_order.customer,
                        title="Entrega Parada",
                        message=f"Seu frete {str(freight_order.id)[:8]} parou em trânsito há mais de {stop_minutes_limit} minutos.",
                        notification_type="stop_detected",
                        metadata={"freight_order_id": str(freight_order.id)}
                    )
        else:
            # Driver is moving! Reset last moving timestamp and stop notification flag
            r.delete(f"tracking:order:{freight_order.id}:last_moving_time")
            r.delete(f"tracking:order:{freight_order.id}:stop_notified")
            
            # If the driver was temporarily stopped, return them to in_transit
            if freight_order.status == 'temporarily_stopped':
                new_status = 'in_transit'
                freight_order.status = 'in_transit'
                freight_order.save(update_fields=['status'])

        # 6. Route Deviation Detection
        # Calculate perpendicular distance to straight line between origin and destination
        # For simplicity, we implement Haversine route deviation from straight line or direct segment
        # In degrees:
        x0, y0 = float(lat_dec), float(lng_dec)
        x1, y1 = float(freight_order.origin_latitude), float(freight_order.origin_longitude)
        x2, y2 = float(freight_order.destination_latitude), float(freight_order.destination_longitude)
        
        # Line segment length
        segment_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if segment_len > 0:
            # Perpendicular distance in degrees
            dist_deg = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1) / segment_len
            # Convert roughly to KM (1 degree is ~111 KM)
            deviation_km = dist_deg * 111.0
            
            deviation_limit = float(getattr(settings, 'ROUTE_DEVIATION_KM', 5.0))
            
            if deviation_km > deviation_limit:
                deviation_notified = r.get(f"tracking:order:{freight_order.id}:deviation_notified")
                if not deviation_notified and freight_order.status in ['in_transit', 'temporarily_stopped']:
                    new_status = 'route_deviation_detected'
                    freight_order.status = 'route_deviation_detected'
                    freight_order.save(update_fields=['status'])
                    
                    r.set(f"tracking:order:{freight_order.id}:deviation_notified", "1")
                    
                    # Create Route Deviation Event
                    TrackingEvent.objects.create(
                        freight_order=freight_order,
                        driver=driver_user,
                        vehicle=freight_order.vehicle,
                        event_type='route_deviation',
                        latitude=lat_dec,
                        longitude=lng_dec,
                        speed=speed_dec,
                        heading=heading_dec,
                        description=f"Desvio de rota detectado. Distância da reta ideal: {round(deviation_km, 2)} km.",
                        previous_status=previous_status,
                        new_status=new_status,
                        created_by=driver_user
                    )
                    
                    # Notify Support Operators and Client
                    NotificationService.send_notification(
                        user=freight_order.customer,
                        title="Desvio de Rota Detectado",
                        message=f"Seu frete {str(freight_order.id)[:8]} apresentou desvio da rota original.",
                        notification_type="route_deviation",
                        metadata={"freight_order_id": str(freight_order.id), "deviation_km": deviation_km}
                    )
            else:
                # Driver is back on route
                r.delete(f"tracking:order:{freight_order.id}:deviation_notified")
                if freight_order.status == 'route_deviation_detected':
                    new_status = 'in_transit'
                    freight_order.status = 'in_transit'
                    freight_order.save(update_fields=['status'])

        # Create general Location Updated Event in database
        event = TrackingEvent.objects.create(
            freight_order=freight_order,
            driver=driver_user,
            vehicle=freight_order.vehicle,
            event_type='location_updated',
            latitude=lat_dec,
            longitude=lng_dec,
            speed=speed_dec,
            heading=heading_dec,
            description="Atualização periódica de localização via telemetria GPS.",
            previous_status=previous_status,
            new_status=new_status,
            created_by=driver_user
        )

        # 7. WebSocket Channel Group Broadcast
        channel_layer = get_channel_layer()
        if channel_layer:
            # A) Notify order specific group
            async_to_sync(channel_layer.group_send)(
                f"tracking_order_{freight_order.id}",
                {
                    "type": "location_update",
                    "freight_order_id": str(freight_order.id),
                    "latitude": str(lat_dec),
                    "longitude": str(lng_dec),
                    "speed": str(speed_dec),
                    "heading": str(heading_dec),
                    "status": new_status,
                    "eta": eta_str
                }
            )
            # B) Notify general customer updates
            async_to_sync(channel_layer.group_send)(
                f"customer_{freight_order.customer.id}",
                {
                    "type": "order_update",
                    "freight_order_id": str(freight_order.id),
                    "status": new_status,
                    "eta": eta_str
                }
            )
            # C) Notify admin operations room
            async_to_sync(channel_layer.group_send)(
                "admin_operations",
                {
                    "type": "operations_update",
                    "freight_order_id": str(freight_order.id),
                    "driver_name": driver_user.name,
                    "latitude": str(lat_dec),
                    "longitude": str(lng_dec),
                    "status": new_status,
                    "eta": eta_str
                }
            )

        return event
