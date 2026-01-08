"""
Models do app Core - Modelo de usuário base do sistema
"""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Gerenciador que impõe autenticação baseada em e-mail."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: object) -> "User":
        """Cria um usuário com email e senha"""
        if not email:
            raise ValueError("O endereço de e-mail deve ser informado.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        """Cria e salva um usuário comum utilizando e-mail e senha."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None, **extra_fields: object) -> "User":
        """Cria e salva um superusuário utilizando e-mail e senha."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuários devem ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuários devem ter is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modelo de usuário customizado sem username, usando e-mail como identificador principal.

    Este é o modelo base de usuário para todo o sistema.
    """

    username = None
    first_name = None
    last_name = None
    email = models.EmailField("email address", unique=True)
    full_name = models.CharField(max_length=255, blank=True, verbose_name=_("Nome completo"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Endereço"))
    city = models.CharField(max_length=128, blank=True, verbose_name=_("Cidade"))
    state = models.CharField(max_length=64, blank=True, verbose_name=_("Estado"))
    phone = models.CharField(max_length=32, blank=True, verbose_name=_("Telefone"))
    theme_preference = models.CharField(
        max_length=10,
        choices=[("light", _("Claro")), ("dark", _("Escuro"))],
        default="light",
        verbose_name=_("Preferência de tema"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects: UserManager = UserManager()

    class Meta:
        """Opções de metadados para o modelo de usuário."""

        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")
        swappable = "AUTH_USER_MODEL"

    def __str__(self) -> str:
        return self.get_full_name() or str(self.email)

    def get_full_name(self) -> str:
        """Retorna o nome completo ou email"""
        cleaned = str(self.full_name or "").strip()
        return cleaned or str(self.email)

    def get_short_name(self) -> str:
        """Retorna o primeiro nome se houver full_name, caso contrário retorna a parte antes do @ do email."""
        cleaned = str(self.full_name or "").strip()
        if cleaned:
            first_name, *_ = cleaned.split(maxsplit=1)
            return first_name
        # Se não tiver nome completo, retorna a parte antes do @ do email
        email_str = str(self.email)
        if "@" in email_str:
            return email_str.split("@")[0]
        return email_str


class OnboardingStatus(models.Model):
    """
    Rastreia o status de onboarding do usuário.
    Armazena informações sobre conclusão e se mensagens foram dispensadas.
    """

    user = models.OneToOneField(
        "core.User",
        on_delete=models.CASCADE,
        related_name="onboarding_status",
        verbose_name=_("Usuário"),
    )
    completion_message_dismissed = models.BooleanField(
        _("Mensagem de conclusão dispensada"),
        default=False,
        help_text=_("Indica se o usuário fechou a mensagem de conclusão do onboarding"),
    )
    dismissed_at = models.DateTimeField(
        _("Data de dispensa"),
        null=True,
        blank=True,
        help_text=_("Data e hora em que a mensagem de conclusão foi dispensada"),
    )
    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Status de Onboarding")
        verbose_name_plural = _("Status de Onboarding")
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Onboarding Status - {self.user.email}"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Obtém ou cria o status de onboarding para um usuário."""
        status, created = cls.objects.get_or_create(user=user)
        return status

    def dismiss_completion_message(self):
        """Marca a mensagem de conclusão como dispensada."""
        from django.utils import timezone

        self.completion_message_dismissed = True
        self.dismissed_at = timezone.now()
        self.save(update_fields=["completion_message_dismissed", "dismissed_at", "updated_at"])









