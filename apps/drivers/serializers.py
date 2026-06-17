import datetime
from rest_framework import serializers
from apps.drivers.models import DriverProfile

class DriverProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for DriverProfile.
    Prevents direct updating of status, ratings, and online states.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    carrier_company_name = serializers.CharField(source='carrier_company.trade_name', read_only=True)

    class Meta:
        model = DriverProfile
        fields = [
            'id', 'user', 'user_name', 'user_email', 'carrier_company', 
            'carrier_company_name', 'cnh_number', 'cnh_category', 
            'cnh_expiration_date', 'rating', 'status', 'current_latitude', 
            'current_longitude', 'is_online', 'accepts_equipment', 
            'accepts_dry_grains', 'pix_key', 'bank_data', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'rating', 'status', 'is_online', 
            'current_latitude', 'current_longitude', 'created_at', 'updated_at'
        ]

    def validate_cnh_expiration_date(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError("A CNH informada já está vencida.")
        return value
