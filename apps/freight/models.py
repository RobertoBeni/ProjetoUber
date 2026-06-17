from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel
from apps.cargo.models import CargoType

class FreightOrder(UUIDModel):
    STATUS_CHOICES = [
        ('requested', 'Solicitado'),
        ('waiting_driver', 'Aguardando Motorista'),
        ('driver_found', 'Motorista Encontrado'),
        ('driver_going_to_pickup', 'Motorista a Caminho da Coleta'),
        ('arrived_at_origin', 'Chegou na Origem'),
        ('cargo_collected', 'Carga Coletada'),
        ('in_transit', 'Em Trânsito'),
        ('temporarily_stopped', 'Parado Temporariamente'),
        ('route_deviation_detected', 'Desvio de Rota Identificado'),
        ('near_destination', 'Próximo ao Destino'),
        ('arrived_at_destination', 'Chegou ao Destino'),
        ('delivered', 'Entregue'),
        ('completed', 'Finalizado'),
        ('cancelled', 'Cancelado'),
        ('disputed', 'Em Disputa'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='freight_orders_as_customer',
        verbose_name="Cliente Embarcador"
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='freight_orders_as_driver',
        verbose_name="Motorista"
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='freight_orders',
        verbose_name="Veículo"
    )
    carrier_company = models.ForeignKey(
        'companies.CarrierCompany',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='freight_orders',
        verbose_name="Transportadora"
    )
    
    # Geographic parameters
    origin_address = models.CharField(
        max_length=255,
        verbose_name="Endereço de Origem"
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
    destination_address = models.CharField(
        max_length=255,
        verbose_name="Endereço de Destino"
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

    # Cargo summary
    cargo_category = models.CharField(
        max_length=30,
        choices=CargoType.CATEGORY_CHOICES,
        verbose_name="Categoria Principal da Carga"
    )
    cargo_description = models.TextField(
        verbose_name="Descrição da Carga"
    )
    estimated_weight_kg = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Peso Estimado (KG)"
    )
    estimated_volume_m3 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Volume Estimado (M³)"
    )
    required_vehicle_type = models.CharField(
        max_length=50,
        verbose_name="Tipo de Veículo Exigido"
    )
    required_body_type = models.CharField(
        max_length=50,
        verbose_name="Tipo de Carroceria Exigida"
    )
    requires_helper = models.BooleanField(
        default=False,
        verbose_name="Exige Ajudante"
    )
    requires_insurance = models.BooleanField(
        default=False,
        verbose_name="Exige Seguro"
    )

    # Operational metrics
    scheduled_pickup_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Coleta Agendada para"
    )
    estimated_distance_km = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Distância Estimada (KM)"
    )
    estimated_duration_minutes = models.PositiveIntegerField(
        verbose_name="Duração Estimada (Minutos)"
    )
    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Estimado"
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Final"
    )
    
    # Tracking status
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='requested',
        verbose_name="Status do Frete"
    )
    estimated_arrival_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Previsão de Chegada (ETA)"
    )
    
    # Timestamps
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Aceito em"
    )
    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Coletado em"
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Entregue em"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelado em"
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de Cancelamento"
    )

    class Meta:
        verbose_name = "Ordem de Frete"
        verbose_name_plural = "Ordens de Fretes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Frete {self.id[:8]}... ({self.get_status_display()})"

class CargoItem(UUIDModel):
    freight_order = models.ForeignKey(
        FreightOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Ordem de Frete"
    )
    cargo_type = models.ForeignKey(
        CargoType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cargo_items',
        verbose_name="Tipo de Carga"
    )
    description = models.CharField(
        max_length=255,
        verbose_name="Descrição do Item"
    )
    estimated_weight_kg = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Peso Estimado (KG)"
    )
    estimated_volume_m3 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Volume Estimado (M³)"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade"
    )
    is_fragile = models.BooleanField(
        default=False,
        verbose_name="Frágil"
    )
    requires_helper = models.BooleanField(
        default=False,
        verbose_name="Requer Ajudante"
    )
    requires_insurance = models.BooleanField(
        default=False,
        verbose_name="Requer Seguro"
    )
    requires_covered_vehicle = models.BooleanField(
        default=False,
        verbose_name="Requer Veículo Coberto / Baú"
    )
    requires_grain_body = models.BooleanField(
        default=False,
        verbose_name="Requer Carroceria Graneleira"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )

    class Meta:
        verbose_name = "Item de Carga"
        verbose_name_plural = "Itens de Cargas"

    def __str__(self):
        return f"Item: {self.description} ({self.quantity}x)"
