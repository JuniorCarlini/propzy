from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LandingsConfig(AppConfig):
    """Configuração do app Landings"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.landings"
    label = "landings"
    verbose_name = _("Landing Pages")

    def ready(self):
        """Importa signals quando o app estiver pronto"""
        import apps.landings.signals  # noqa: F401
