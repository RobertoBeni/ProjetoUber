from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.eta.models import ETARecord

class ETAService:
    """
    Service for dynamically estimating and updating arrival times (ETA) based on
    vehicle speeds, remaining distances, and cargo-specific handling or stops (such as weighing scales).
    """
    @staticmethod
    def calculate_and_update_eta(freight_order, remaining_distance_km=None, reason="inicialização"):
        if remaining_distance_km is None:
            # First calculation or default to estimated distance
            remaining_distance_km = freight_order.estimated_distance_km or Decimal("10.00")
            
        # Determine average speed based on vehicle type and cargo category
        # Heavy trucks (e.g. for grains) go slower (50 km/h), lighter utility vehicles go faster (70 km/h)
        if freight_order.cargo_category == 'DRY_GRAINS':
            average_speed_kmh = Decimal("50.00")
            extra_delays_minutes = 30  # Weighing scale check (parada de balança)
        else:
            average_speed_kmh = Decimal("60.00")
            extra_delays_minutes = 15  # Careful handling margin
            
        # Time remaining in minutes = (distance / speed) * 60
        travel_duration_minutes = int((float(remaining_distance_km) / float(average_speed_kmh)) * 60)
        total_remaining_minutes = travel_duration_minutes + extra_delays_minutes
        
        # Calculate ETA timestamp
        now = timezone.now()
        estimated_arrival = now + timedelta(minutes=total_remaining_minutes)
        
        # Create ETA Record
        eta_record = ETARecord.objects.create(
            freight_order=freight_order,
            estimated_arrival_time=estimated_arrival,
            remaining_distance_km=Decimal(str(remaining_distance_km)),
            remaining_duration_minutes=total_remaining_minutes,
            average_speed_kmh=average_speed_kmh,
            reason=reason
        )
        
        # Update freight order ETA
        freight_order.estimated_arrival_time = estimated_arrival
        freight_order.save(update_fields=['estimated_arrival_time'])
        
        return eta_record
