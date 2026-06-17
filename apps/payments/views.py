from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.payments.models import Payment
from apps.payments.serializers import PaymentSerializer
from apps.payments.services import PaymentService

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing virtual financial payments and simulating clearing confirmations.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()
        if user.is_superuser or user.is_staff:
            return Payment.objects.all()
        if user.user_type == 'DRIVER':
            return Payment.objects.filter(driver=user)
        return Payment.objects.filter(payer=user)

    @action(detail=True, methods=['post'], url_path='simulate-confirmation')
    def simulate_confirmation(self, request, pk=None):
        payment = self.get_object()
        if payment.status != 'pending':
            return Response(
                {"detail": f"O pagamento já está com status: {payment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        confirmed_payment = PaymentService.simulate_payment_confirmation(payment)
        serializer = self.get_serializer(confirmed_payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
