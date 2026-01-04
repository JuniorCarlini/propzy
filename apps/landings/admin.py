"""
Admin do app Landings.

Configuração da interface administrativa para gerenciar:
- Temas
- Landing Pages
- Imóveis
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import LandingPage, LandingPageTheme, Property, PropertyImage


@admin.register(LandingPageTheme)
class LandingPageThemeAdmin(admin.ModelAdmin):
    """Admin para temas de landing pages"""

    list_display = ["name", "slug", "category", "version", "is_active", "is_premium", "order"]
    list_filter = ["category", "is_active", "is_premium"]
    search_fields = ["name", "slug", "description", "author"]
    prepopulated_fields = {"slug": ("name",)}
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


class PropertyImageInline(admin.TabularInline):
    """Inline para imagens adicionais do imóvel"""

    model = PropertyImage
    extra = 3
    fields = ["image", "caption", "order"]


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin para imóveis"""

    list_display = [
        "title",
        "landing_page",
        "property_type",
        "transaction_type",
        "city",
        "state",
        "is_featured",
        "is_active",
        "created_at",
    ]
    list_filter = ["property_type", "transaction_type", "is_featured", "is_active", "state", "city", "created_at"]
    search_fields = ["title", "description", "address", "neighborhood", "city"]
    list_editable = ["is_featured", "is_active"]
    date_hierarchy = "created_at"
    inlines = [PropertyImageInline]

    fieldsets = (
        (
            _("Landing Page"),
            {
                "fields": ("landing_page",),
            },
        ),
        (
            _("Informações Básicas"),
            {
                "fields": ("title", "description", "property_type", "transaction_type", "main_image"),
            },
        ),
        (
            _("Valores"),
            {
                "fields": ("sale_price", "rent_price"),
            },
        ),
        (
            _("Características"),
            {
                "fields": ("bedrooms", "bathrooms", "garage_spaces", "area"),
            },
        ),
        (
            _("Localização"),
            {
                "fields": ("address", "neighborhood", "city", "state", "zipcode"),
            },
        ),
        (
            _("Configurações"),
            {
                "fields": ("is_featured", "is_active", "order"),
            },
        ),
    )

    def get_queryset(self, request):
        """Otimiza query"""
        qs = super().get_queryset(request)
        return qs.select_related("landing_page", "landing_page__owner")


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    """Admin para landing pages"""

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
                "fields": ("business_name", "business_description"),
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



