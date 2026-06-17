from rest_framework import viewsets, permissions
from apps.eta.models import ETARecord
from apps.eta.serializers import ETARecordSerializer

class ETARecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for query history of ETA dynamic recalculation records.
    """
    queryset = ETARecord.objects.all()
    serializer_class = ETARecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ETARecord.objects.none()
        if user.is_superuser or user.is_staff:
            return ETARecord.objects.all()
        if user.user_type == 'DRIVER':
            return ETARecord.objects.filter(freight_order__driver=user)
        return ETARecord.objects.filter(freight_order__customer=user)
