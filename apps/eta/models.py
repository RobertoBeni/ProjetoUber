from django.db import models
from apps.core.models import UUIDModel
from apps.freight.models import FreightOrder

class ETARecord(UUIDModel):
    freight_order = models.ForeignKey(
        FreightOrder,
        on_delete=models.CASCADE,
        related_name='eta_records',
        verbose_name="Ordem de Frete"
    )
    estimated_arrival_time = models.DateTimeField(
        verbose_name="Previsão de Chegada Estimada"
    )
    remaining_distance_km = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Distância Restante (KM)"
    )
    remaining_duration_minutes = models.PositiveIntegerField(
        verbose_name="Duração Restante (Minutos)"
    )
    average_speed_kmh = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=60.00,
        verbose_name="Velocidade Média (KM/H)"
    )
    reason = models.CharField(
        max_length=255,
        default="inicialização",
        verbose_name="Motivo do Recálculo"
    )

    class Meta:
        verbose_name = "Registro de ETA"
        verbose_name_plural = "Registros de ETAs"
        ordering = ['-created_at']

    def __str__(self):
        return f"ETA para Frete {self.freight_order.id[:8]}... - {self.estimated_arrival_time}"
