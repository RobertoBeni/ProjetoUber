from rest_framework import serializers
from apps.matching.models import MatchCandidate

class MatchCandidateSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    driver_phone = serializers.CharField(source='driver.phone', read_only=True)
    driver_rating = serializers.DecimalField(source='driver.driver_profile.rating', max_digits=3, decimal_places=2, read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    vehicle_model = serializers.CharField(source='vehicle.model', read_only=True)
    
    class Meta:
        model = MatchCandidate
        fields = [
            'id', 'freight_order', 'driver', 'driver_name', 'driver_phone', 'driver_rating',
            'vehicle', 'vehicle_plate', 'vehicle_model', 'distance_to_pickup_km', 
            'compatibility_score', 'proximity_score', 'rating_score', 'final_score', 
            'status', 'created_at', 'updated_at'
        ]
