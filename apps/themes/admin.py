"""
Admin do app Themes
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Theme


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Admin para temas de landing pages"""

    list_display = ["name", "slug", "category", "version", "is_active", "is_premium", "order"]
    list_filter = ["category", "is_active", "is_premium"]
    search_fields = ["name", "slug", "description", "author"]
    ordering = ["order", "name"]

    fieldsets = (
        (
            _("Informações Básicas"),
            {
                "fields": ("name", "slug", "description", "author", "version", "category"),
            },
        ),
        (
            _("Aparência"),
            {
                "fields": ("screenshot", "default_primary_color", "default_secondary_color"),
            },
        ),
        (
            _("Configurações"),
            {
                "fields": ("is_active", "is_premium", "order", "features"),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        """Torna slug readonly após criação"""
        if obj:  # Editando
            return ["slug"]
        return []

    def get_prepopulated_fields(self, request, obj=None):
        """Aplica prepopulated_fields apenas na criação"""
        if obj is None:  # Criando novo
            return {"slug": ("name",)}
        return {}
