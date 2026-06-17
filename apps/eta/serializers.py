from rest_framework import serializers
from apps.eta.models import ETARecord

class ETARecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETARecord
        fields = [
            'id', 'freight_order', 'estimated_arrival_time', 'remaining_distance_km',
            'remaining_duration_minutes', 'average_speed_kmh', 'reason', 'created_at'
        ]
