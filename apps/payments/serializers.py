from rest_framework import serializers
from apps.payments.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    payer_name = serializers.CharField(source='payer.name', read_only=True)
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'freight_order', 'payer', 'payer_name', 'driver', 'driver_name',
            'amount', 'platform_fee', 'driver_amount', 'status', 'payment_method',
            'transaction_id', 'paid_at', 'created_at', 'updated_at'
        ]
