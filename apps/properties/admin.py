"""
Admin do app Properties
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Property, PropertyImage


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
        "site",
        "property_type",
        "category",
        "transaction_type",
        "city",
        "state",
        "is_featured",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "property_type",
        "category",
        "transaction_type",
        "is_featured",
        "is_active",
        "state",
        "city",
        "created_at",
    ]
    search_fields = ["title", "description", "address", "neighborhood", "city"]
    list_editable = ["is_featured", "is_active"]
    date_hierarchy = "created_at"
    inlines = [PropertyImageInline]

    fieldsets = (
        (
            _("Site"),
            {
                "fields": ("site",),
            },
        ),
        (
            _("Informações Básicas"),
            {
                "fields": ("title", "description", "property_type", "category", "transaction_type", "main_image"),
            },
        ),
        (
            _("Valores"),
            {
                "fields": ("sale_price", "rent_price", "original_sale_price", "original_rent_price"),
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
        return qs.select_related("site", "site__owner")


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Admin para imagens de imóveis"""

    list_display = ["property", "order", "caption", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["property__title", "caption"]
    ordering = ["property", "order"]
