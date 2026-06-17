from rest_framework import serializers
from apps.pricing.models import PriceEstimate

class PriceEstimateInputSerializer(serializers.Serializer):
    origin_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    origin_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    cargo_type_slug = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    requires_helper = serializers.BooleanField(required=False, default=False)
    requires_insurance = serializers.BooleanField(required=False, default=False)

class PriceEstimateSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    cargo_type_name = serializers.CharField(source='cargo_type.name', read_only=True)
    
    class Meta:
        model = PriceEstimate
        fields = [
            'id', 'customer', 'customer_name', 'origin_latitude', 'origin_longitude', 
            'destination_latitude', 'destination_longitude', 'cargo_type', 'cargo_type_name',
            'vehicle_type', 'distance_km', 'duration_minutes', 'base_fee', 'distance_fee', 
            'time_fee', 'helper_fee', 'insurance_fee', 'urgency_fee', 'risk_fee', 
            'toll_fee', 'availability_fee', 'total_estimated_price', 'breakdown', 'created_at'
        ]
