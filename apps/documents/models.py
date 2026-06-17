from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class Document(UUIDModel):
    DOCUMENT_TYPES = [
        ('CNH', 'Carteira Nacional de Habilitação'),
        ('CRLV', 'Certificado de Registro e Licenciamento do Veículo'),
        ('INVOICE', 'Nota Fiscal da Carga'),
        ('WEIGHING', 'Ticket de Pesagem'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendente de Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Proprietário do Documento"
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        verbose_name="Tipo do Documento"
    )
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        verbose_name="Arquivo"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Revisado em"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents',
        verbose_name="Revisado por"
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo da Rejeição"
    )

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.owner.name} ({self.status})"
