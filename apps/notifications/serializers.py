from rest_framework import serializers
from apps.notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type', 'is_read', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'title', 'message', 'notification_type', 'metadata', 'created_at']
