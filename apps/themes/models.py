"""
Models do app Themes - Sistema de temas para landing pages
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.Model):
    """
    Representa um tema instalado no sistema.
    Os temas ficam em templates/landings/themes/<slug>/
    """

    # Identificação
    name = models.CharField(_("Nome"), max_length=100)
    slug = models.SlugField(
        _("Slug"), max_length=50, unique=True, help_text=_("Nome da pasta do tema. Ex: modern, classic")
    )

    # Metadados
    description = models.TextField(_("Descrição"), blank=True)
    author = models.CharField(_("Autor"), max_length=100, blank=True)
    version = models.CharField(_("Versão"), max_length=20, default="1.0.0")

    # Categorização
    CATEGORIES = [
        ("modern", _("Moderno")),
        ("classic", _("Clássico")),
        ("minimal", _("Minimalista")),
        ("luxury", _("Luxuoso")),
        ("corporate", _("Corporativo")),
    ]
    category = models.CharField(_("Categoria"), max_length=20, choices=CATEGORIES, default="modern")

    # Preview
    screenshot = models.ImageField(
        _("Screenshot"), upload_to="themes/screenshots/", blank=True, help_text=_("Preview do tema")
    )

    # Cores padrão (podem ser sobrescritas pelo usuário)
    default_primary_color = models.CharField(_("Cor Primária Padrão"), max_length=7, default="#007bff")
    default_secondary_color = models.CharField(_("Cor Secundária Padrão"), max_length=7, default="#6c757d")

    # Status
    is_active = models.BooleanField(_("Ativo"), default=True, help_text=_("Se desativado, não aparece para seleção"))
    is_premium = models.BooleanField(_("Premium"), default=False, help_text=_("Requer plano premium"))

    # Ordem de exibição
    order = models.PositiveIntegerField(_("Ordem"), default=0)

    # Metadados técnicos
    features = models.JSONField(_("Recursos"), default=list, blank=True, help_text=_("Lista de recursos do tema"))

    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Tema")
        verbose_name_plural = _("Temas")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def get_template_path(self, template_name: str = "index.html") -> str:
        """Retorna o caminho do template"""
        return f"landings/themes/{self.slug}/{template_name}"

    def get_theme_dir(self) -> Path:
        """Retorna o diretório do tema"""
        base_template_dir = Path(settings.BASE_DIR) / "templates"
        return base_template_dir / "landings" / "themes" / self.slug

    def get_theme_config(self) -> dict:
        """Lê o arquivo theme.json do tema"""
        theme_dir = self.get_theme_dir()
        config_file = theme_dir / "theme.json"

        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def validate_theme_exists(self):
        """Valida se a pasta do tema existe"""
        theme_dir = self.get_theme_dir()
        if not theme_dir.exists():
            raise ValidationError(f"Pasta do tema não encontrada: {theme_dir}")

        # Valida se tem pelo menos index.html
        index_file = theme_dir / "index.html"
        if not index_file.exists():
            raise ValidationError(f"Arquivo index.html não encontrado no tema: {self.slug}")

    def clean(self):
        """Validação customizada"""
        super().clean()
        # Só valida se o tema já existe (em modo produção)
        # Em desenvolvimento, permite criar o tema antes da pasta
        if not settings.DEBUG:
            self.validate_theme_exists()
















