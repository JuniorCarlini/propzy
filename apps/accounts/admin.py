from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import AdminUserChangeForm, AdminUserCreationForm
from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Exibe e gerencia usuários no painel administrativo do Django."""

    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    model = User
    ordering = ("email",)
    list_display = ("email", "full_name", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "full_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Informações pessoais"),
            {"fields": ("full_name", "phone", "address", "city", "state")},
        ),
        (
            _("Permissões"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (_("Datas importantes"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "phone",
                    "address",
                    "city",
                    "state",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )
