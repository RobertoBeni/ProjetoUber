from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class CompanyProfile(UUIDModel):
    """
    Profile for generic corporate clients (Pessoa Jurídica).
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente de Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('suspended', 'Suspenso'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_profile',
        verbose_name="Usuário Proprietário"
    )
    legal_name = models.CharField(
        max_length=255,
        verbose_name="Razão Social"
    )
    trade_name = models.CharField(
        max_length=255,
        verbose_name="Nome Fantasia"
    )
    cnpj = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="CNPJ"
    )
    state_registration = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Inscrição Estadual"
    )
    responsible_name = models.CharField(
        max_length=255,
        verbose_name="Nome do Responsável"
    )
    responsible_phone = models.CharField(
        max_length=20,
        verbose_name="Telefone do Responsável"
    )
    billing_address = models.TextField(
        verbose_name="Endereço de Faturamento"
    )
    operational_address = models.TextField(
        verbose_name="Endereço Operacional"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )

    class Meta:
        verbose_name = "Perfil de Empresa (PJ)"
        verbose_name_plural = "Perfis de Empresas (PJ)"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.trade_name} ({self.cnpj})"

class CarrierCompany(UUIDModel):
    """
    Profile for registered carrier companies (Transportadoras).
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente de Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('suspended', 'Suspenso'),
    ]

    owner_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrier_company',
        verbose_name="Dono da Transportadora"
    )
    legal_name = models.CharField(
        max_length=255,
        verbose_name="Razão Social"
    )
    trade_name = models.CharField(
        max_length=255,
        verbose_name="Nome Fantasia"
    )
    cnpj = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="CNPJ"
    )
    state_registration = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Inscrição Estadual"
    )
    responsible_name = models.CharField(
        max_length=255,
        verbose_name="Nome do Responsável"
    )
    responsible_phone = models.CharField(
        max_length=20,
        verbose_name="Telefone do Responsável"
    )
    billing_address = models.TextField(
        verbose_name="Endereço de Faturamento"
    )
    operational_address = models.TextField(
        verbose_name="Endereço Operacional"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )

    class Meta:
        verbose_name = "Transportadora"
        verbose_name_plural = "Transportadoras"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.trade_name} ({self.cnpj})"
