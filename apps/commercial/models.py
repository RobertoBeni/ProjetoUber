import uuid
from django.db import models
from apps.core.models import UUIDModel

class InvestorLead(UUIDModel):
    PROFILE_CHOICES = [
        ('investor', 'Investidor'),
        ('carrier', 'Transportadora'),
        ('shipper', 'Embarcador'),
        ('partner', 'Parceiro Comercial'),
        ('press', 'Imprensa'),
        ('other', 'Outro'),
    ]

    INTEREST_CHOICES = [
        ('low', 'Baixo'),
        ('medium', 'Médio'),
        ('high', 'Alto'),
        ('strategic', 'Estratégico'),
    ]

    STATUS_CHOICES = [
        ('new', 'Novo'),
        ('contacted', 'Contatado'),
        ('meeting_scheduled', 'Reunião Agendada'),
        ('negotiating', 'Em Negociação'),
        ('converted', 'Convertido'),
        ('lost', 'Perdido'),
    ]

    name = models.CharField(max_length=255, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="E-mail de Contato")
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Telefone")
    company = models.CharField(max_length=255, blank=True, default="", verbose_name="Empresa / Organização")
    profile_type = models.CharField(
        max_length=30,
        choices=PROFILE_CHOICES,
        default='other',
        verbose_name="Perfil do Lead"
    )
    estimated_interest_level = models.CharField(
        max_length=20,
        choices=INTEREST_CHOICES,
        default='medium',
        verbose_name="Nível de Interesse Estimado"
    )
    message = models.TextField(blank=True, default="", verbose_name="Mensagem / Comentário")
    source_page = models.CharField(max_length=255, default="/", verbose_name="Página de Origem")
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Status de Atendimento"
    )
    notes = models.TextField(blank=True, default="", verbose_name="Notas de Acompanhamento Interno")

    class Meta:
        verbose_name = "Lead Comercial / Investidor"
        verbose_name_plural = "Leads Comerciais / Investidores"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.company or 'S/E'}) - {self.get_profile_type_display()}"
