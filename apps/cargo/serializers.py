from rest_framework import serializers
from apps.cargo.models import CargoType, CargoRule

class CargoRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for CargoRule.
    """
    class Meta:
        model = CargoRule
        fields = [
            'id', 'recommended_vehicle_types', 'required_body_types', 
            'requires_covered_vehicle', 'requires_grain_body', 
            'requires_helper_recommended', 'requires_insurance_recommended', 
            'requires_lashing', 'requires_tarp', 'requires_invoice', 
            'requires_weighing', 'handling_instructions'
        ]

class CargoTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for CargoType including its linked CargoRule details.
    """
    rule = CargoRuleSerializer(read_only=True)

    class Meta:
        model = CargoType
        fields = [
            'id', 'name', 'category', 'slug', 'description', 
            'is_active', 'rule', 'created_at', 'updated_at'
        ]
