from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import User


@login_required
def index_view(request):
    """Renderiza a página inicial."""

    # Estatísticas básicas
    total_users = User.objects.filter(is_active=True).count() if request.user.has_perm("accounts.view_user") else 0
    total_groups = Group.objects.count() if request.user.has_perm("auth.view_group") else 0
    total_projects = 0  # Será implementado quando houver app de projetos

    context = {
        "total_users": total_users,
        "total_groups": total_groups,
        "total_projects": total_projects,
    }

    return render(request, "main/index.html", context)


@login_required
@require_POST
def toggle_theme_view(request):
    """Alterna o tema do usuário e redireciona de volta."""

    current_theme = request.user.theme_preference
    new_theme = "dark" if current_theme == "light" else "light"

    request.user.theme_preference = new_theme
    request.user.save(update_fields=["theme_preference"])

    return redirect(request.META.get("HTTP_REFERER", "/"))
