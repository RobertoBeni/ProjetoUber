import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel

class UserManager(BaseUserManager):
    """
    Custom manager for the custom User model supporting login via email.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo E-mail é obrigatório.")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        # Default document types/numbers if blank to prevent db issues
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, UUIDModel):
    """
    Custom User model with standard parameters for FreteHub.
    Uses email as primary login identity.
    """
    DOCUMENT_TYPES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
    ]

    USER_TYPES = [
        ('PF', 'Cliente Pessoa Física'),
        ('PJ', 'Cliente Pessoa Jurídica'),
        ('DRIVER', 'Motorista'),
        ('CARRIER', 'Transportadora'),
        ('ADMIN', 'Administrador'),
        ('SUPPORT', 'Operador de Suporte'),
        ('FINANCE', 'Operador Financeiro'),
        ('LOGISTICS', 'Operador Logístico'),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name="Nome Completo / Razão Social"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="E-mail"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone"
    )
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPES,
        default='CPF',
        verbose_name="Tipo de Documento"
    )
    document_number = models.CharField(
        max_length=25,
        blank=True,
        verbose_name="Número do Documento"
    )
    user_type = models.CharField(
        max_length=15,
        choices=USER_TYPES,
        default='PF',
        verbose_name="Tipo de Usuário"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff"
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Superusuário"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"

class UserConsent(UUIDModel):
    CONSENT_TYPES = [
        ('terms_of_service', 'Termos de Uso'),
        ('privacy_policy', 'Política de Privacidade'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consents',
        verbose_name="Usuário"
    )
    consent_type = models.CharField(
        max_length=50,
        choices=CONSENT_TYPES,
        verbose_name="Tipo de Consentimento"
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name="Aceito"
    )
    version = models.CharField(
        max_length=20,
        default="1.0",
        verbose_name="Versão"
    )
    accepted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Aceito em"
    )
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        verbose_name="Endereço IP"
    )

    class Meta:
        verbose_name = "Consentimento do Usuário"
        verbose_name_plural = "Consentimentos do Usuário"
        ordering = ['-accepted_at']

    def __str__(self):
        return f"{self.user.name} - {self.get_consent_type_display()} v{self.version} ({'Aceito' if self.accepted else 'Recusado'})"
