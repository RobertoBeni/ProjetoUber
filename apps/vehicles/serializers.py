import datetime
from rest_framework import serializers
from apps.vehicles.models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for Vehicle model representation and validation.
    Prevents direct updating of status and ownership fields.
    """
    owner_email = serializers.EmailField(source='owner_driver.email', read_only=True)
    carrier_company_name = serializers.CharField(source='carrier_company.trade_name', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner_driver', 'owner_email', 'carrier_company', 
            'carrier_company_name', 'plate', 'renavam', 'brand', 
            'model', 'year', 'vehicle_type', 'body_type', 'max_weight_kg', 
            'max_volume_m3', 'allowed_cargo_types', 'has_insurance', 
            'insurance_policy_number', 'status', 'current_latitude', 
            'current_longitude', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner_driver', 'status', 'created_at', 'updated_at']

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if value < current_year - 40:  # Allow up to 40 years old for robust local fleets
            raise serializers.ValidationError("Veículos com mais de 40 anos não são aceitos na plataforma.")
        return value
