import uuid
from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class AIConversation(UUIDModel):
    CHANNEL_CHOICES = [
        ('web', 'Portal Web'),
        ('mobile', 'Aplicativo Mobile'),
        ('admin', 'Painel Administrativo'),
        ('driver_app', 'App do Motorista'),
        ('carrier_portal', 'Portal da Transportadora'),
    ]

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('closed', 'Fechado'),
        ('escalated', 'Escalonado para Humano'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        verbose_name="Usuário"
    )
    channel = models.CharField(
        max_length=25,
        choices=CHANNEL_CHOICES,
        default='web',
        verbose_name="Canal de Origem"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Status"
    )

    class Meta:
        verbose_name = "Conversa com IA"
        verbose_name_plural = "Conversas com IA"
        ordering = ['-created_at']

    def __str__(self):
        return f"Conversa {self.id[:8]}... - {self.user.name} ({self.get_status_display()})"

class AIMessage(UUIDModel):
    SENDER_CHOICES = [
        ('user', 'Usuário'),
        ('assistant', 'Assistente IA'),
        ('system', 'Sistema'),
        ('human_agent', 'Atendente Humano'),
    ]

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Conversa"
    )
    sender = models.CharField(
        max_length=20,
        choices=SENDER_CHOICES,
        verbose_name="Remetente"
    )
    message_text = models.TextField(
        verbose_name="Texto da Mensagem"
    )
    intent = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Intenção Identificada"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=1.0000,
        verbose_name="Confiança da Intenção"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados da Resposta"
    )

    class Meta:
        verbose_name = "Mensagem da Conversa"
        verbose_name_plural = "Mensagens da Conversa"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_sender_display()}: {self.message_text[:40]}..."

class AIAction(UUIDModel):
    STATUS_CHOICES = [
        ('pending', 'Pendente de Confirmação'),
        ('confirmed', 'Confirmado pelo Usuário'),
        ('executed', 'Executado'),
        ('cancelled', 'Cancelado'),
        ('failed', 'Falhou'),
    ]

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="Conversa"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_actions_triggered',
        verbose_name="Usuário"
    )
    action_type = models.CharField(
        max_length=100,
        verbose_name="Tipo de Ação"
    )
    target_entity = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Entidade Alvo"
    )
    target_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID do Alvo"
    )
    status = models.DynamicField = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status da Ação"
    )
    requires_confirmation = models.BooleanField(
        default=True,
        verbose_name="Exige Confirmação"
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Confirmado em"
    )

    class Meta:
        verbose_name = "Ação da IA"
        verbose_name_plural = "Ações da IA"
        ordering = ['-created_at']

    def __str__(self):
        return f"Ação {self.action_type} ({self.status})"

class KnowledgeDocument(UUIDModel):
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('published', 'Publicado'),
        ('archived', 'Arquivado'),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name="Título do Artigo"
    )
    category = models.CharField(
        max_length=100,
        verbose_name="Categoria"
    )
    content = models.TextField(
        verbose_name="Conteúdo do Artigo"
    )
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name="Versão"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='published',
        verbose_name="Status de Publicação"
    )

    class Meta:
        verbose_name = "Artigo de Conhecimento"
        verbose_name_plural = "Artigos de Conhecimento"
        ordering = ['category', 'title']

    def __str__(self):
        return f"[{self.category}] {self.title} (v{self.version})"

class KnowledgeEmbedding(UUIDModel):
    document = models.ForeignKey(
        KnowledgeDocument,
        on_delete=models.CASCADE,
        related_name='embeddings',
        verbose_name="Documento"
    )
    embedding_vector = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Vetor de Embedding"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados do Fragmento"
    )

    class Meta:
        verbose_name = "Embedding de Conhecimento"
        verbose_name_plural = "Embeddings de Conhecimento"

    def __str__(self):
        return f"Embedding para {self.document.title}"
