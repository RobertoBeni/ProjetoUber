from rest_framework import serializers
from apps.tracking.models import TrackingEvent

class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent
        fields = '__all__'
        read_only_fields = ('created_at',)

class TelemetryPayloadSerializer(serializers.Serializer):
    freight_order_id = serializers.UUIDField(required=True)
    driver_id = serializers.UUIDField(required=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    speed = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    heading = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    timestamp = serializers.DateTimeField(required=False, allow_null=True)
