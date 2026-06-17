from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing and reading internal operational notifications.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users only see their own notifications, Admins see all
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()
        if user.is_superuser or user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(user=user)

    @action(detail=True, methods=['patch', 'post'], url_path='read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
