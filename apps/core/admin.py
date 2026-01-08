"""
Admin do app Core
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import OnboardingStatus, User


@admin.register(OnboardingStatus)
class OnboardingStatusAdmin(admin.ModelAdmin):
    """Admin para Status de Onboarding"""

    list_display = ("user", "completion_message_dismissed", "dismissed_at", "updated_at")
    list_filter = ("completion_message_dismissed", "dismissed_at", "created_at")
    search_fields = ("user__email", "user__full_name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            _("Informações do Usuário"),
            {
                "fields": ("user",),
            },
        ),
        (
            _("Status de Mensagens"),
            {
                "fields": ("completion_message_dismissed", "dismissed_at"),
            },
        ),
        (
            _("Datas"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin customizado para o modelo de usuário"""

    list_display = ["email", "full_name", "is_staff", "is_active", "date_joined"]
    list_filter = ["is_staff", "is_superuser", "is_active", "date_joined"]
    search_fields = ["email", "full_name", "phone"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Informações Pessoais"), {"fields": ("full_name", "phone", "address", "city", "state")}),
        (
            _("Permissões"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Preferências"), {"fields": ("theme_preference",)}),
        (_("Datas Importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )










