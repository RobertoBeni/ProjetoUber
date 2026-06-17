from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class DriverProfile(UUIDModel):
    """
    Operational profile for registered system Drivers.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente de Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('suspended', 'Suspenso'),
    ]

    CNH_CATEGORIES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('AB', 'AB'),
        ('AC', 'AC'),
        ('AD', 'AD'),
        ('AE', 'AE'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        verbose_name="Usuário"
    )
    carrier_company = models.ForeignKey(
        'companies.CarrierCompany',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers',
        verbose_name="Transportadora Vinculada"
    )
    cnh_number = models.CharField(
        max_length=20,
        verbose_name="Número da CNH"
    )
    cnh_category = models.CharField(
        max_length=5,
        choices=CNH_CATEGORIES,
        verbose_name="Categoria da CNH"
    )
    cnh_expiration_date = models.DateField(
        verbose_name="Validade da CNH"
    )
    rating = models.DecimalField(
        max_length=5,
        max_digits=3,
        decimal_places=2,
        default=5.00,
        verbose_name="Avaliação do Motorista"
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
    is_online = models.BooleanField(
        default=False,
        verbose_name="Online"
    )
    accepts_equipment = models.BooleanField(
        default=True,
        verbose_name="Transporta Equipamentos / Móveis"
    )
    accepts_dry_grains = models.BooleanField(
        default=False,
        verbose_name="Transporta Grãos Secos"
    )
    pix_key = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Chave PIX"
    )
    bank_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Dados Bancários"
    )

    class Meta:
        verbose_name = "Perfil de Motorista"
        verbose_name_plural = "Perfis de Motoristas"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} (CNH: {self.cnh_number})"
