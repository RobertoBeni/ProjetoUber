import datetime
from decimal import Decimal
from django.db.models import Q
from apps.drivers.models import DriverProfile
from apps.vehicles.models import Vehicle
from apps.matching.models import MatchCandidate
from apps.routing.services import RoutingService

class MatchingService:
    """
    Service for calculating matching scores and ranking drivers based on
    vehicle type, weight/volume capacity, geographical proximity, ratings, and active status.
    """
    @staticmethod
    def find_and_rank_candidates(freight_order):
        # 1. Get online, approved drivers with valid CNH
        today = datetime.date.today()
        drivers = DriverProfile.objects.filter(
            is_online=True,
            status='approved',
            cnh_expiration_date__gte=today
        )

        candidates_created = []

        # Delete existing pending candidates for this order to avoid duplicates
        MatchCandidate.objects.filter(freight_order=freight_order, status='pending').delete()

        for driver_profile in drivers:
            user = driver_profile.user
            
            # Check cargo category match
            if freight_order.cargo_category == 'DRY_GRAINS' and not driver_profile.accepts_dry_grains:
                continue
            if freight_order.cargo_category == 'EQUIPMENTS' and not driver_profile.accepts_equipment:
                continue

            # 2. Get approved vehicle(s) for this driver
            vehicles = Vehicle.objects.filter(
                owner_driver=user,
                status='approved'
            )

            for vehicle in vehicles:
                # 3. Check physical capabilities
                if vehicle.max_weight_kg < freight_order.estimated_weight_kg:
                    continue
                if vehicle.max_volume_m3 < freight_order.estimated_volume_m3:
                    continue

                # Check if coordinates exist to calculate proximity
                if driver_profile.current_latitude is None or driver_profile.current_longitude is None:
                    # Default coordinates if none specified
                    driver_lat = freight_order.origin_latitude + Decimal("0.05")
                    driver_lng = freight_order.origin_longitude + Decimal("0.05")
                else:
                    driver_lat = driver_profile.current_latitude
                    driver_lng = driver_profile.current_longitude

                # Calculate proximity distance using Haversine
                distance_to_pickup = RoutingService.haversine_distance(
                    driver_lat, driver_lng,
                    freight_order.origin_latitude, freight_order.origin_longitude
                )

                # Proximity score (0-100)
                if distance_to_pickup < 2:
                    proximity_score = Decimal("100.00")
                elif distance_to_pickup < 5:
                    proximity_score = Decimal("80.00")
                elif distance_to_pickup < 10:
                    proximity_score = Decimal("60.00")
                elif distance_to_pickup < 20:
                    proximity_score = Decimal("40.00")
                else:
                    proximity_score = Decimal("20.00")

                # Rating score (0-100) - based on rating 0 to 5
                rating = driver_profile.rating or Decimal("5.00")
                rating_score = rating * Decimal("20.00")

                # Compatibility score (0-100)
                comp_score = Decimal("50.00")  # Base compatibility if passed filtering
                if vehicle.vehicle_type == freight_order.required_vehicle_type:
                    comp_score += Decimal("25.00")
                if vehicle.body_type == freight_order.required_body_type:
                    comp_score += Decimal("25.00")

                # Final weighted score: (Rating * 0.3) + (Proximity * 0.4) + (Compatibility * 0.3)
                final_score = (rating_score * Decimal("0.30")) + (proximity_score * Decimal("0.40")) + (comp_score * Decimal("0.30"))

                # Create Match Candidate record
                candidate = MatchCandidate.objects.create(
                    freight_order=freight_order,
                    driver=user,
                    vehicle=vehicle,
                    distance_to_pickup_km=Decimal(str(round(distance_to_pickup, 2))),
                    compatibility_score=comp_score,
                    proximity_score=proximity_score,
                    rating_score=rating_score,
                    final_score=final_score.quantize(Decimal("0.01")),
                    status='pending'
                )
                candidates_created.append(candidate)

        # Sort candidate list descending by final_score
        candidates_created.sort(key=lambda x: x.final_score, reverse=True)
        return candidates_created
