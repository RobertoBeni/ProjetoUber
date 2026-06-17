import math
from decimal import Decimal
from apps.routing.models import Route

class RoutingService:
    """
    Service for simulating route generation based on coordinates, implementing
    geographical haversine distances with terrestrial buffer additions (+15%).
    """
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        # Convert latitude and longitude to spherical coordinates in radians.
        degrees_to_radians = math.pi / 180.0
            
        phi1 = float(lat1) * degrees_to_radians
        phi2 = float(lat2) * degrees_to_radians
            
        theta1 = float(lon1) * degrees_to_radians
        theta2 = float(lon2) * degrees_to_radians
            
        dphi = phi2 - phi1
        dtheta = theta2 - theta1
        
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dtheta / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        r = 6371.0  # Radius of earth in kilometers
        
        return r * c

    @staticmethod
    def calculate_simulated_route(origin_lat, origin_lng, dest_lat, dest_lng):
        dist = RoutingService.haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
        # Add 15% terrestrial margin
        distance_km = dist * 1.15
        
        # Estimate duration: average speed 60 km/h (1 min per km), let's use 1.2 min per km
        duration_minutes = int(max(5, round(distance_km * 1.2)))
        
        # Estimate toll
        toll_estimate = 18.0 if distance_km > 20 else 0.0
        
        return {
            'distance_km': round(distance_km, 2),
            'duration_minutes': duration_minutes,
            'polyline': 'encoded_polyline_placeholder',
            'toll_estimate': toll_estimate,
            'restrictions': {
                'max_height_meters': 4.2,
                'max_weight_tons': 23.0
            }
        }

    @staticmethod
    def create_route_for_order(freight_order):
        route_data = RoutingService.calculate_simulated_route(
            freight_order.origin_latitude,
            freight_order.origin_longitude,
            freight_order.destination_latitude,
            freight_order.destination_longitude
        )
        
        route = Route.objects.create(
            freight_order=freight_order,
            origin_latitude=freight_order.origin_latitude,
            origin_longitude=freight_order.origin_longitude,
            destination_latitude=freight_order.destination_latitude,
            destination_longitude=freight_order.destination_longitude,
            distance_km=Decimal(str(route_data['distance_km'])),
            duration_minutes=route_data['duration_minutes'],
            polyline=route_data['polyline'],
            toll_estimate=Decimal(str(route_data['toll_estimate'])),
            restrictions=route_data['restrictions']
        )
        return route
