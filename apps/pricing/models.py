from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel
from apps.cargo.models import CargoType

class PriceEstimate(UUIDModel):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='price_estimates',
        verbose_name="Cliente"
    )
    origin_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Latitude de Origem"
    )
    origin_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Longitude de Origem"
    )
    destination_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Latitude de Destino"
    )
    destination_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Longitude de Destino"
    )
    cargo_type = models.ForeignKey(
        CargoType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Carga"
    )
    vehicle_type = models.CharField(
        max_length=50,
        verbose_name="Tipo de Veículo Recomendado"
    )
    distance_km = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Distância (KM)"
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name="Duração (Minutos)"
    )
    
    # Financial breakdown fields
    base_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Tarifa Base"
    )
    distance_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Distância"
    )
    time_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Tempo"
    )
    helper_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Ajudante"
    )
    insurance_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Seguro"
    )
    urgency_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Urgência"
    )
    risk_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Risco de Rota"
    )
    toll_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Estimativa de Pedágios"
    )
    availability_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taxa de Disponibilidade"
    )
    total_estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Total Estimado"
    )
    breakdown = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Breakdown Detalhado"
    )

    class Meta:
        verbose_name = "Estimativa de Preço"
        verbose_name_plural = "Estimativas de Preços"
        ordering = ['-created_at']

    def __str__(self):
        return f"Estimativa {self.id[:8]}... - Total: R$ {self.total_estimated_price}"
