"""
Sistema de permissões compartilhado
"""
from typing import Final, cast

from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

# Apps que devem exibir permissões no sistema
DISPLAYABLE_PERMISSION_APPS: Final[tuple[str, ...]] = (
    "core",
    "administration",
    "landings",
    "properties",
    "themes",
    "auth",
)

# Labels amigáveis para cada app
PERMISSION_APP_LABELS: Final[dict[str, str]] = {
    "core": cast(str, _("Sistema Core")),
    "administration": cast(str, _("Administração")),
    "landings": cast(str, _("Landing Pages")),
    "properties": cast(str, _("Imóveis")),
    "themes": cast(str, _("Temas")),
    "auth": cast(str, _("Controle de acesso")),
}

# Labels para ações de permissão
ACTION_LABELS: Final[dict[str, str]] = {
    "add": cast(str, _("Adicionar %(object)s")),
    "change": cast(str, _("Editar %(object)s")),
    "delete": cast(str, _("Excluir %(object)s")),
    "view": cast(str, _("Visualizar %(object)s")),
}


def get_permission_group_label(app_label: str) -> str:
    """Retorna um rótulo amigável para o namespace de permissões."""
    default_label = app_label.replace("_", " ").title()
    label = PERMISSION_APP_LABELS.get(app_label)
    if label is not None:
        return str(label)
    return default_label


def get_permission_object_name(permission: Permission) -> str:
    """Retorna o nome descritivo do modelo associado à permissão."""
    model_class = permission.content_type.model_class()  # type: ignore[attr-defined]
    if model_class is not None:
        codename_str = str(permission.codename)
        if codename_str.startswith("view_"):
            verbose_name = model_class._meta.verbose_name_plural
        else:
            verbose_name = model_class._meta.verbose_name
        return str(verbose_name)
    return str(permission.name)


def format_permission_label(permission: Permission) -> str:
    """Monta um rótulo amigável e bilíngue para a permissão."""
    codename_str = str(permission.codename)
    action = codename_str.split("_", 1)[0]
    model_name = get_permission_object_name(permission)
    template = ACTION_LABELS.get(action)
    if template:
        return str(template % {"object": model_name})
    fallback = _("%(action)s %(object)s")
    return str(fallback % {"action": action.capitalize(), "object": model_name})


def is_displayable_permission(permission: Permission) -> bool:
    """Informa se a permissão pertence a um namespace exibível no sistema."""
    app_label = str(permission.content_type.app_label)  # type: ignore[attr-defined]
    return app_label in DISPLAYABLE_PERMISSION_APPS


















