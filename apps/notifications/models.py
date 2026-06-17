from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class Notification(UUIDModel):
    NOTIFICATION_TYPES = [
        ('freight_requested', 'Frete Solicitado'),
        ('driver_found', 'Motorista Encontrado'),
        ('driver_accepted', 'Motorista Aceitou o Frete'),
        ('arrived_origin', 'Motorista Chegou na Coleta'),
        ('cargo_collected', 'Carga Coletada'),
        ('in_transit', 'Carga em Trânsito'),
        ('eta_updated', 'Previsão ETA Alterada'),
        ('delivered', 'Entrega Realizada'),
        ('payment_confirmed', 'Pagamento Confirmado'),
        ('alert', 'Alerta Operacional'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Usuário Destinatário"
    )
    title = models.CharField(
        max_length=150,
        verbose_name="Título"
    )
    message = models.TextField(
        verbose_name="Mensagem"
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default='alert',
        verbose_name="Tipo da Notificação"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Lida"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados da Notificação"
    )

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificação para {self.user.name}: {self.title} (Lida: {self.is_read})"
