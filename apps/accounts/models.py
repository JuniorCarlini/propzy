from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Gerenciador que impõe autenticação baseada em e-mail."""

    # Definir posteriormente quais campos adicionais serão necessários

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: object) -> "User":
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
    """Modelo de usuário sem username, usando e-mail como identificador principal."""

    username = None
    first_name = None
    last_name = None
    email = models.EmailField("email address", unique=True)
    full_name = models.CharField(max_length=255, blank=True, verbose_name=_("Nome completo"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Endereço"))
    city = models.CharField(max_length=128, blank=True, verbose_name=_("Cidade"))
    state = models.CharField(max_length=64, blank=True, verbose_name=_("Estado"))
    phone = models.CharField(max_length=32, blank=True, verbose_name=_("Telefone"))

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
        cleaned = str(self.full_name or "").strip()
        return cleaned or str(self.email)

    def get_short_name(self) -> str:
        cleaned = str(self.full_name or "").strip()
        if cleaned:
            first_name, *_ = cleaned.split(maxsplit=1)
            return first_name
        return str(self.email)
