import uuid
from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel
from apps.freight.models import FreightOrder
from apps.vehicles.models import Vehicle

class TrackingEvent(UUIDModel):
    EVENT_TYPES = [
        ('order_created', 'Pedido Criado'),
        ('driver_accepted', 'Motorista Aceitou'),
        ('driver_arrived_origin', 'Motorista Chegou à Origem'),
        ('cargo_collected', 'Carga Coletada'),
        ('route_started', 'Rota Iniciada'),
        ('location_updated', 'Localização Atualizada'),
        ('stop_detected', 'Parada Detectada'),
        ('route_deviation', 'Desvio de Rota'),
        ('risk_area_entered', 'Entrada em Área de Risco'),
        ('arrived_destination', 'Chegada ao Destino'),
        ('delivery_confirmed', 'Entrega Confirmada'),
        ('occurrence_registered', 'Ocorrência Registrada'),
    ]

    freight_order = models.ForeignKey(
        FreightOrder,
        on_delete=models.CASCADE,
        related_name='tracking_events',
        verbose_name="Ordem de Frete"
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_tracking_events',
        verbose_name="Motorista"
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicle_tracking_events',
        verbose_name="Veículo"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        default='location_updated',
        verbose_name="Tipo do Evento"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude"
    )
    speed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Velocidade (km/h)"
    )
    heading = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Direção (Graus)"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    image = models.FileField(
        upload_to='tracking/photos/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="Foto da Ocorrência / Comprovante"
    )
    signature = models.FileField(
        upload_to='tracking/signatures/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="Assinatura Digital"
    )
    previous_status = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Status Anterior"
    )
    new_status = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Novo Status"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tracking_events',
        verbose_name="Criado Por"
    )

    class Meta:
        verbose_name = "Evento de Rastreamento"
        verbose_name_plural = "Eventos de Rastreamento"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.freight_order.id[:8]} - {self.get_event_type_display()} ({self.created_at})"
