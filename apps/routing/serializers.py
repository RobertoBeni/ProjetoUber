from rest_framework import serializers
from apps.routing.models import Route

class RouteCalculateInputSerializer(serializers.Serializer):
    origin_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    origin_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            'id', 'freight_order', 'provider', 'origin_latitude', 'origin_longitude', 
            'destination_latitude', 'destination_longitude', 'distance_km', 
            'duration_minutes', 'polyline', 'toll_estimate', 'restrictions'
        ]
