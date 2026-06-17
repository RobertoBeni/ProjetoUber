from rest_framework import serializers
from decimal import Decimal
from apps.freight.models import FreightOrder, CargoItem
from apps.cargo.models import CargoType

class CargoItemSerializer(serializers.ModelSerializer):
    cargo_type_slug = serializers.CharField(write_only=True, required=False)
    cargo_type_name = serializers.CharField(source='cargo_type.name', read_only=True)
    
    class Meta:
        model = CargoItem
        fields = [
            'id', 'cargo_type_slug', 'cargo_type_name', 'description', 
            'estimated_weight_kg', 'estimated_volume_m3', 'quantity', 
            'is_fragile', 'requires_helper', 'requires_insurance', 
            'requires_covered_vehicle', 'requires_grain_body', 'notes'
        ]

class FreightOrderSerializer(serializers.ModelSerializer):
    items = CargoItemSerializer(many=True, required=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    carrier_company_name = serializers.CharField(source='carrier_company.trade_name', read_only=True)
    
    class Meta:
        model = FreightOrder
        fields = [
            'id', 'customer', 'customer_name', 'driver', 'driver_name', 
            'vehicle', 'vehicle_plate', 'carrier_company', 'carrier_company_name',
            'origin_address', 'origin_latitude', 'origin_longitude', 
            'destination_address', 'destination_latitude', 'destination_longitude', 
            'cargo_category', 'cargo_description', 'estimated_weight_kg', 
            'estimated_volume_m3', 'required_vehicle_type', 'required_body_type', 
            'requires_helper', 'requires_insurance', 'scheduled_pickup_at', 
            'estimated_distance_km', 'estimated_duration_minutes', 'estimated_price', 
            'final_price', 'status', 'estimated_arrival_time', 'accepted_at', 
            'picked_up_at', 'delivered_at', 'cancelled_at', 'cancellation_reason',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer', 'driver', 'vehicle', 'carrier_company', 
            'estimated_weight_kg', 'estimated_volume_m3', 'required_vehicle_type', 
            'required_body_type', 'requires_helper', 'requires_insurance', 
            'estimated_distance_km', 'estimated_duration_minutes', 'estimated_price', 
            'final_price', 'status', 'estimated_arrival_time', 'accepted_at', 
            'picked_up_at', 'delivered_at', 'cancelled_at', 'cancellation_reason',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        customer = request.user
        
        from apps.freight.services import FreightService
        freight_order = FreightService.create_freight_order(
            customer=customer,
            origin_address=validated_data.get('origin_address'),
            origin_latitude=Decimal(str(validated_data.get('origin_latitude'))),
            origin_longitude=Decimal(str(validated_data.get('origin_longitude'))),
            destination_address=validated_data.get('destination_address'),
            destination_latitude=Decimal(str(validated_data.get('destination_latitude'))),
            destination_longitude=Decimal(str(validated_data.get('destination_longitude'))),
            cargo_category=validated_data.get('cargo_category'),
            cargo_description=validated_data.get('cargo_description'),
            items_data=items_data,
            scheduled_pickup_at=validated_data.get('scheduled_pickup_at')
        )
        return freight_order
