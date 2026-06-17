from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel
from apps.freight.models import FreightOrder
from apps.vehicles.models import Vehicle

class MatchCandidate(UUIDModel):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('notified', 'Notificado'),
        ('accepted', 'Aceito'),
        ('rejected', 'Rejeitado'),
        ('expired', 'Expirado'),
    ]

    freight_order = models.ForeignKey(
        FreightOrder,
        on_delete=models.CASCADE,
        related_name='candidates',
        verbose_name="Ordem de Frete"
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matching_candidacies',
        verbose_name="Motorista Candidato"
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='matching_candidacies',
        verbose_name="Veículo Utilizado"
    )
    distance_to_pickup_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Distância até Coleta (KM)"
    )
    
    # Matching Scores breakdown
    compatibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score de Compatibilidade"
    )
    proximity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score de Proximidade"
    )
    rating_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score de Avaliação"
    )
    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score Final de Matching"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status da Candidatura"
    )

    class Meta:
        verbose_name = "Candidato de Matching"
        verbose_name_plural = "Candidatos de Matching"
        ordering = ['-final_score']

    def __str__(self):
        return f"Match: {self.driver.name} -> Score {self.final_score} ({self.status})"
