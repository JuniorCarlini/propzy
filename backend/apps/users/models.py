import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.tenants.models import Tenant


class UserManager(BaseUserManager):
    """Manager customizado para User com email como username"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modelo de Usuário customizado.
    
    Características:
    - Email como campo de login (não username)
    - Vinculado a um tenant
    - Email único apenas por tenant (não globalmente)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_('Tenant')
    )
    email = models.EmailField(unique=False, verbose_name=_('Email'))
    username = None  # Remover username
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remover username dos campos obrigatórios
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        unique_together = [['tenant', 'email']]  # Email único por tenant
        indexes = [
            models.Index(fields=['tenant', 'email']),
        ]

    def __str__(self):
        return f"{self.email} ({self.tenant.name})"

