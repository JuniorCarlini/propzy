"""
Admin do app Landings - Site

NOTA: Admins movidos para seus respectivos apps:
- ThemeAdmin → apps.themes.admin
- PropertyAdmin → apps.properties.admin
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    """Admin para sites"""

    list_display = [
        "business_name",
        "owner",
        "subdomain_link",
        "custom_domain_link",
        "theme",
        "is_published",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "is_published", "theme", "created_at"]
    search_fields = ["business_name", "subdomain", "custom_domain", "owner__email"]
    list_editable = ["is_published", "is_active"]
    date_hierarchy = "created_at"
    raw_id_fields = ["owner"]

    fieldsets = (
        (
            _("Proprietário"),
            {
                "fields": ("owner",),
            },
        ),
        (
            _("Domínios"),
            {
                "fields": ("subdomain", "custom_domain"),
                "description": _("Configure o subdomínio e/ou domínio personalizado"),
            },
        ),
        (
            _("Tema e Aparência"),
            {
                "fields": ("theme", "logo", "hero_image", "primary_color", "secondary_color"),
            },
        ),
        (
            _("Dados do Negócio"),
            {
                "fields": ("business_name",),
            },
        ),
        (
            _("Contato"),
            {
                "fields": ("email", "phone", "whatsapp"),
            },
        ),
        (
            _("Endereço"),
            {
                "fields": ("address", "city", "state"),
            },
        ),
        (
            _("Redes Sociais"),
            {
                "fields": ("facebook_url", "instagram_url", "linkedin_url"),
            },
        ),
        (
            _("SEO"),
            {
                "fields": ("meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active", "is_published"),
            },
        ),
    )

    def subdomain_link(self, obj):
        """Exibe link do subdomínio"""
        url = f"https://{obj.get_full_subdomain()}"
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.get_full_subdomain())

    subdomain_link.short_description = _("Subdomínio")

    def custom_domain_link(self, obj):
        """Exibe link do domínio personalizado"""
        if obj.custom_domain:
            url = f"https://{obj.custom_domain}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.custom_domain)
        return "-"

    custom_domain_link.short_description = _("Domínio Personalizado")

    def get_queryset(self, request):
        """Otimiza query"""
        qs = super().get_queryset(request)
        return qs.select_related("owner", "theme")
