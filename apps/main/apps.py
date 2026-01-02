from django.apps import AppConfig


class MainConfig(AppConfig):
    """Attach metadata for the main application."""

    default_auto_field: str = "django.db.models.BigAutoField"  # type: ignore[assignment]
    name = "apps.main"
    label = "main"  # Define explicitamente o app_label usado em referências de modelos
    verbose_name = "Dashboard"
