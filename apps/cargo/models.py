from django.db import models
from apps.core.models import UUIDModel

class CargoType(UUIDModel):
    """
    Subtypes of cargo categorized under Equipments or Dry Grains.
    """
    CATEGORY_CHOICES = [
        ('EQUIPMENTS', 'Equipamentos e Móveis'),
        ('DRY_GRAINS', 'Grãos Secos'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Nome da Carga"
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name="Categoria Principal"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Slug"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Tipo de Carga"
        verbose_name_plural = "Tipos de Cargas"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class CargoRule(UUIDModel):
    """
    Compatibility and logistical requirements associated with a specific CargoType.
    """
    cargo_type = models.OneToOneField(
        CargoType,
        on_delete=models.CASCADE,
        related_name='rule',
        verbose_name="Tipo de Carga"
    )
    recommended_vehicle_types = models.JSONField(
        default=list,
        verbose_name="Tipos de Veículos Recomendados"
    )
    required_body_types = models.JSONField(
        default=list,
        verbose_name="Tipos de Carrocerias Exigidas"
    )
    requires_covered_vehicle = models.BooleanField(
        default=False,
        verbose_name="Exige Veículo Coberto / Baú"
    )
    requires_grain_body = models.BooleanField(
        default=False,
        verbose_name="Exige Carroceria Graneleira"
    )
    requires_helper_recommended = models.BooleanField(
        default=False,
        verbose_name="Recomenda Ajudante"
    )
    requires_insurance_recommended = models.BooleanField(
        default=False,
        verbose_name="Recomenda Seguro de Carga"
    )
    requires_lashing = models.BooleanField(
        default=False,
        verbose_name="Exige Amarração de Carga"
    )
    requires_tarp = models.BooleanField(
        default=False,
        verbose_name="Exige Cobertura com Lona"
    )
    requires_invoice = models.BooleanField(
        default=False,
        verbose_name="Exige Nota Fiscal"
    )
    requires_weighing = models.BooleanField(
        default=False,
        verbose_name="Exige Pesagem em Balança"
    )
    handling_instructions = models.TextField(
        blank=True,
        verbose_name="Instruções de Manuseio"
    )

    class Meta:
        verbose_name = "Regra de Carga"
        verbose_name_plural = "Regras de Cargas"

    def __str__(self):
        return f"Regra: {self.cargo_type.name}"
