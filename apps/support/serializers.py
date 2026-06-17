from rest_framework import serializers
from apps.support.models import SupportTicket

class SupportTicketSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_from_display = serializers.CharField(source='get_created_from_display', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True, default="")
    freight_order_code = serializers.CharField(source='freight_order.id', read_only=True, default="")

    class Meta:
        model = SupportTicket
        fields = [
            'id', 'user', 'user_name', 'freight_order', 'freight_order_code', 
            'assigned_to', 'assigned_to_name', 'category', 'category_display', 
            'priority', 'priority_display', 'status', 'status_display', 
            'description', 'created_from', 'created_from_display', 
            'closed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'assigned_to_name', 'category_display', 
            'priority_display', 'status_display', 'created_from_display', 
            'closed_at', 'created_at', 'updated_at'
        ]
