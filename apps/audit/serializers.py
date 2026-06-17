from rest_framework import serializers
from apps.audit.models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for representing AuditLog records.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action', 'entity_type', 
            'entity_id', 'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
