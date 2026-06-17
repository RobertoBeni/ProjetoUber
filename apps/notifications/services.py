from apps.notifications.models import Notification

class NotificationService:
    """
    Service for dispatching internal system notifications and tracking delivery / read status.
    """
    @staticmethod
    def send_notification(user, title, message, notification_type='alert', metadata=None):
        if metadata is None:
            metadata = {}
            
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            metadata=metadata
        )
        # Here we could easily integrate third-party push/SMS or Django Channels
        return notification
