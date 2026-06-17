from django.db import models
from apps.core.models import UUIDModel
from apps.freight.models import FreightOrder

class Route(UUIDModel):
    freight_order = models.OneToOneField(
        FreightOrder,
        on_delete=models.CASCADE,
        related_name='route_details',
        verbose_name="Ordem de Frete"
    )
    provider = models.CharField(
        max_length=50,
        default='mock',
        verbose_name="Provedor de Mapas"
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
    distance_km = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Distância Terrestre (KM)"
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name="Duração da Rota (Minutos)"
    )
    polyline = models.TextField(
        blank=True,
        verbose_name="Encoded Polyline da Rota"
    )
    toll_estimate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name="Estimativa de Pedágios"
    )
    restrictions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Restrições Operacionais (Altura/Peso)"
    )

    class Meta:
        verbose_name = "Rota do Frete"
        verbose_name_plural = "Rotas dos Fretes"

    def __str__(self):
        return f"Rota para Frete {self.freight_order.id[:8]}... - {self.distance_km} KM"
