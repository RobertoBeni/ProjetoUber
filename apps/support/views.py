from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.support.models import SupportTicket
from apps.support.serializers import SupportTicketSerializer
from django.utils import timezone

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='close')
    def close_ticket(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == 'closed':
            return Response({"detail": "Este ticket já está fechado."}, status=status.HTTP_400_BAD_REQUEST)
        
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save(update_fields=['status', 'closed_at'])
        return Response(SupportTicketSerializer(ticket).data, status=status.HTTP_200_OK)
