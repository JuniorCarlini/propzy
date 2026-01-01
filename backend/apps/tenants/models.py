import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Plan(models.TextChoices):
    """Planos de assinatura disponíveis"""
    FREE = 'free', _('Free')
    BASIC = 'basic', _('Basic')
    PROFESSIONAL = 'professional', _('Professional')
    ENTERPRISE = 'enterprise', _('Enterprise')


class Tenant(models.Model):
    """Modelo de Tenant (Cliente)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_('Nome'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    plan = models.CharField(
        max_length=20,
        choices=Plan.choices,
        default=Plan.FREE,
        verbose_name=_('Plano')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Ativo'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de Criação'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Data de Atualização'))

    class Meta:
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['-created_at']

    def __str__(self):
        return self.name



