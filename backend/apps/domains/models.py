import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.tenants.models import Tenant


class DomainType(models.TextChoices):
    """Tipos de domínio"""
    SUBDOMAIN = 'subdomain', _('Subdomínio')
    CUSTOM = 'custom', _('Domínio Personalizado')


class Domain(models.Model):
    """Modelo de Domínio"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='domains',
        verbose_name=_('Tenant')
    )
    domain = models.CharField(max_length=255, unique=True, verbose_name=_('Domínio'))
    type = models.CharField(
        max_length=20,
        choices=DomainType.choices,
        default=DomainType.SUBDOMAIN,
        verbose_name=_('Tipo')
    )
    is_verified = models.BooleanField(default=False, verbose_name=_('Verificado'))
    verification_token = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=_('Token de Verificação')
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Verificado em'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de Criação'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Data de Atualização'))

    class Meta:
        verbose_name = _('Domínio')
        verbose_name_plural = _('Domínios')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.domain} ({self.tenant.name})"



