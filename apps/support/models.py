import uuid
from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel
from apps.freight.models import FreightOrder

class SupportTicket(UUIDModel):
    CATEGORY_CHOICES = [
        ('atraso', 'Atraso na Entrega'),
        ('carga_danificada', 'Carga Danificada / Avaria'),
        ('pagamento', 'Problema com Pagamento'),
        ('documento', 'Problema com Documentação'),
        ('motorista', 'Problema com Motorista'),
        ('cliente', 'Problema com Cliente'),
        ('divergencia_peso', 'Divergência de Peso / Volume'),
        ('cancelamento', 'Problema com Cancelamento'),
        ('problema_tecnico', 'Instabilidade / Problema Técnico'),
        ('outro', 'Outros Assuntos'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    STATUS_CHOICES = [
        ('open', 'Aberto'),
        ('in_progress', 'Em Atendimento'),
        ('waiting_user', 'Aguardando Usuário'),
        ('resolved', 'Resolvido'),
        ('closed', 'Fechado'),
    ]

    CREATED_FROM_CHOICES = [
        ('portal', 'Portal Web'),
        ('app', 'Aplicativo Mobile'),
        ('ai', 'Assistente de IA'),
        ('admin', 'Painel Administrativo'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets',
        verbose_name="Usuário Solicitante"
    )
    freight_order = models.ForeignKey(
        FreightOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_tickets',
        verbose_name="Ordem de Frete Relacionada"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_support_tickets',
        verbose_name="Atendente Responsável"
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='outro',
        verbose_name="Categoria"
    )
    priority = models.CharField(
        max_length=15,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Prioridade"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name="Status"
    )
    description = models.TextField(
        verbose_name="Descrição do Chamado"
    )
    created_from = models.CharField(
        max_length=15,
        choices=CREATED_FROM_CHOICES,
        default='portal',
        verbose_name="Origem de Criação"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fechado em"
    )

    class Meta:
        verbose_name = "Ticket de Suporte"
        verbose_name_plural = "Tickets de Suporte"
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.id[:8]}... [{self.get_category_display()}] - {self.user.name} ({self.get_status_display()})"
