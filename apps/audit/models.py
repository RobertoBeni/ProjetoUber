from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class AuditLog(UUIDModel):
    """
    System audit logging model to capture key system activities and changes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Usuário"
    )
    action = models.CharField(
        max_length=100,
        verbose_name="Ação"
    )
    entity_type = models.CharField(
        max_length=100,
        verbose_name="Tipo de Entidade"
    )
    entity_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID da Entidade"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Endereço IP"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="User Agent"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados adicionais"
    )

    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.email if self.user else "Anônimo"
        return f"[{self.created_at}] {user_str} - {self.action} ({self.entity_type})"
