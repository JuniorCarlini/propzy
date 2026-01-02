from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Set default metadata for the accounts app."""

    default_auto_field: str = "django.db.models.BigAutoField"  # type: ignore[assignment]
    name = "apps.accounts"
    label = "accounts"  # Define explicitamente o app_label usado em referências de modelos
    verbose_name = "Contas"
