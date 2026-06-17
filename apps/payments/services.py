import uuid
from decimal import Decimal
from django.utils import timezone
from apps.payments.models import Payment

class PaymentService:
    """
    Service for virtual billing, transaction generation, and simulated payment clearing
    which unlocks requested freights into active matching queues.
    """
    @staticmethod
    def create_payment_for_order(freight_order, payment_method='pix'):
        amount = freight_order.estimated_price or Decimal("0.00")
        
        # Intermediate platform fee is 15%
        platform_fee = (amount * Decimal("0.15")).quantize(Decimal("0.01"))
        driver_amount = (amount - platform_fee).quantize(Decimal("0.01"))
        
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        payment = Payment.objects.create(
            freight_order=freight_order,
            payer=freight_order.customer,
            driver=freight_order.driver,
            amount=amount,
            platform_fee=platform_fee,
            driver_amount=driver_amount,
            status='pending',
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        return payment

    @staticmethod
    def simulate_payment_confirmation(payment):
        # 1. Update payment to Paid
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.save(update_fields=['status', 'paid_at'])
        
        # 2. Advance freight order status to waiting_driver
        freight_order = payment.freight_order
        if freight_order.status == 'requested':
            freight_order.status = 'waiting_driver'
            freight_order.save(update_fields=['status'])
            
            # Trigger dynamic Matching ranking right away!
            from apps.matching.services import MatchingService
            MatchingService.find_and_rank_candidates(freight_order)
            
            # Send Notification that freight is active
            from apps.notifications.services import NotificationService
            NotificationService.send_notification(
                user=freight_order.customer,
                title="Pagamento Confirmado",
                message=f"Seu frete {str(freight_order.id)[:8]} foi pago com sucesso e agora busca motoristas.",
                notification_type="PAYMENT_CONFIRMED",
                metadata={"freight_order_id": str(freight_order.id)}
            )
            
        return payment
