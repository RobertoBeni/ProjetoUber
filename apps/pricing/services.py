import math
from decimal import Decimal
from apps.cargo.models import CargoType
from apps.pricing.models import PriceEstimate
from apps.routing.services import RoutingService

class PricingService:
    """
    Service for dynamic pricing estimation, calculating tariffs, additional fees
    based on cargo requirements, risk areas, toll estimates, and availability.
    """
    @staticmethod
    def calculate_estimate(customer, origin_lat, origin_lng, dest_lat, dest_lng, cargo_type_slug=None, requires_helper=False, requires_insurance=False):
        # 1. Fetch route metrics (distance, duration)
        route_data = RoutingService.calculate_simulated_route(origin_lat, origin_lng, dest_lat, dest_lng)
        distance_km = Decimal(str(route_data['distance_km']))
        duration_minutes = route_data['duration_minutes']
        
        # 2. Get CargoType rules
        cargo_type = None
        recommended_vehicle = "PICKUP"
        if cargo_type_slug:
            try:
                cargo_type = CargoType.objects.get(slug=cargo_type_slug, is_active=True)
                rule = cargo_type.rule
                if rule.recommended_vehicle_types:
                    recommended_vehicle = rule.recommended_vehicle_types[0]
                if rule.requires_helper_recommended:
                    requires_helper = True
                if rule.requires_insurance_recommended:
                    requires_insurance = True
            except Exception:
                pass

        # 3. Base pricing parameters
        base_fee = Decimal("50.00")
        distance_rate = Decimal("2.50")  # R$ 2.50 per KM
        time_rate = Decimal("0.50")      # R$ 0.50 per minute
        
        distance_fee = distance_km * distance_rate
        time_fee = Decimal(str(duration_minutes)) * time_rate
        
        # 4. Cargo and operational additions
        helper_fee = Decimal("120.00") if requires_helper else Decimal("0.00")
        insurance_fee = Decimal("45.00") if requires_insurance else Decimal("0.00")
        
        # Simulated toll & operational risk rates
        toll_fee = Decimal("18.00") if distance_km > 20 else Decimal("0.00")
        risk_fee = Decimal("35.00") if distance_km > 50 else Decimal("0.00")
        urgency_fee = Decimal("0.00")
        availability_fee = Decimal("15.00") if distance_km < 10 else Decimal("0.00") # local surcharge
        
        # Calculate total
        total_estimated_price = (
            base_fee + distance_fee + time_fee + helper_fee + 
            insurance_fee + urgency_fee + risk_fee + toll_fee + availability_fee
        )
        
        # Round up decimal values nicely
        base_fee = base_fee.quantize(Decimal("0.01"))
        distance_fee = distance_fee.quantize(Decimal("0.01"))
        time_fee = time_fee.quantize(Decimal("0.01"))
        helper_fee = helper_fee.quantize(Decimal("0.01"))
        insurance_fee = insurance_fee.quantize(Decimal("0.01"))
        urgency_fee = urgency_fee.quantize(Decimal("0.01"))
        risk_fee = risk_fee.quantize(Decimal("0.01"))
        toll_fee = toll_fee.quantize(Decimal("0.01"))
        availability_fee = availability_fee.quantize(Decimal("0.01"))
        total_estimated_price = total_estimated_price.quantize(Decimal("0.01"))

        breakdown = {
            "base_fee": str(base_fee),
            "distance_fee": str(distance_fee),
            "time_fee": str(time_fee),
            "helper_fee": str(helper_fee),
            "insurance_fee": str(insurance_fee),
            "urgency_fee": str(urgency_fee),
            "risk_fee": str(risk_fee),
            "toll_fee": str(toll_fee),
            "availability_fee": str(availability_fee)
        }

        # Create database record
        estimate = PriceEstimate.objects.create(
            customer=customer,
            origin_latitude=origin_lat,
            origin_longitude=origin_lng,
            destination_latitude=dest_lat,
            destination_longitude=dest_lng,
            cargo_type=cargo_type,
            vehicle_type=recommended_vehicle,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            base_fee=base_fee,
            distance_fee=distance_fee,
            time_fee=time_fee,
            helper_fee=helper_fee,
            insurance_fee=insurance_fee,
            urgency_fee=urgency_fee,
            risk_fee=risk_fee,
            toll_fee=toll_fee,
            availability_fee=availability_fee,
            total_estimated_price=total_estimated_price,
            breakdown=breakdown
        )
        
        return estimate
