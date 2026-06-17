from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel
from apps.freight.models import FreightOrder

class Payment(UUIDModel):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('authorized', 'Autorizado'),
        ('paid', 'Pago'),
        ('failed', 'Falhou'),
        ('refunded', 'Reembolsado'),
        ('cancelled', 'Cancelado'),
    ]

    PAYMENT_METHODS = [
        ('pix', 'PIX'),
        ('card', 'Cartão de Crédito'),
        ('boleto', 'Boleto Bancário'),
        ('invoice', 'Faturamento / Fatura (PJ)'),
    ]

    freight_order = models.ForeignKey(
        FreightOrder,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Ordem de Frete"
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_made',
        verbose_name="Pagador"
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_received',
        verbose_name="Motorista Beneficiário"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Pago"
    )
    platform_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Intermediação"
    )
    driver_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Repassado ao Motorista"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status do Pagamento"
    )
    payment_method = models.CharField(
        max_length=15,
        choices=PAYMENT_METHODS,
        default='pix',
        verbose_name="Método de Pagamento"
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID da Transação Financeira"
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Pagamento"
    )

    class Meta:
        verbose_name = "Pagamento de Frete"
        verbose_name_plural = "Pagamentos de Fretes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pagamento {self.id[:8]}... - Valor: R$ {self.amount} ({self.status})"
