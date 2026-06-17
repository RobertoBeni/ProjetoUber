from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class Vehicle(UUIDModel):
    """
    Vehicle model representing freight transport assets in the system.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente de Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('suspended', 'Suspenso'),
    ]

    VEHICLE_TYPES = [
        # General cargo & Appliances
        ('SMALL_UTILITY', 'Utilitário Pequeno'),
        ('PICKUP', 'Picape / Caminhonete'),
        ('FIORINO', 'Fiorino / Furgão Pequeno'),
        ('VAN', 'Van de Carga'),
        ('LIGHT_TRUCK', 'Caminhão Leve (3/4)'),
        ('MEDIUM_TRUCK', 'Caminhão Médio (Toco)'),
        ('TRUCK', 'Caminhão Pesado (Truck)'),
        ('BOX_TRUCK', 'Caminhão Baú'),
        ('SIDER_TRUCK', 'Caminhão Sider'),
        # Dry Grains (Agro)
        ('GRAIN_TRUCK', 'Caminhão Graneleiro'),
        ('GRAIN_TRAILER', 'Carreta Graneleira (LS)'),
        ('GRAIN_BITREM', 'Bitrem Graneleiro'),
        ('GRAIN_RODOTREM', 'Rodotrem Graneleiro'),
        ('GRAIN_DUMP_TRUCK', 'Caçamba / Truck Basculante'),
    ]

    BODY_TYPES = [
        ('BOX', 'Baú (Fechado)'),
        ('OPEN', 'Grade Aberta'),
        ('SIDER', 'Sider (Lona Lateral)'),
        ('GRAIN', 'Graneleiro (Com Fominha)'),
        ('DUMP', 'Caçamba (Basculante)'),
        ('PLATFORM', 'Prancha / Plataforma'),
        ('REFRIGERATED', 'Frigorífico / Refrigerado'),
    ]

    owner_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_vehicles',
        verbose_name="Motorista Proprietário"
    )
    carrier_company = models.ForeignKey(
        'companies.CarrierCompany',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        verbose_name="Transportadora"
    )
    plate = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Placa"
    )
    renavam = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="RENAVAM"
    )
    brand = models.CharField(
        max_length=100,
        verbose_name="Marca"
    )
    model = models.CharField(
        max_length=100,
        verbose_name="Modelo"
    )
    year = models.PositiveIntegerField(
        verbose_name="Ano de Fabricação"
    )
    vehicle_type = models.CharField(
        max_length=30,
        choices=VEHICLE_TYPES,
        verbose_name="Tipo de Veículo"
    )
    body_type = models.CharField(
        max_length=30,
        choices=BODY_TYPES,
        verbose_name="Tipo de Carroceria"
    )
    max_weight_kg = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Capacidade de Peso (KG)"
    )
    max_volume_m3 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Capacidade de Volume (M³)"
    )
    allowed_cargo_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de Carga Permitidos"
    )
    has_insurance = models.BooleanField(
        default=False,
        verbose_name="Possui Seguro"
    )
    insurance_policy_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número da Apólice de Seguro"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    current_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude Atual"
    )
    current_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude Atual"
    )

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate})"
