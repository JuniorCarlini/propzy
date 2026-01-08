"""
Views do app Core
"""

from typing import Any

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods, require_POST

from .forms import UserPasswordChangeForm, UserProfileForm
from .models import OnboardingStatus


def home(request: HttpRequest) -> HttpResponse:
    """
    Página inicial simples na raiz do projeto.
    Só é exibida quando não há um site válido detectado pelo middleware.
    """
    return render(request, "core/home.html")


def root_view(request: HttpRequest) -> HttpResponse:
    """
    View intermediária que decide qual página mostrar:
    - Se for um site válido (request.is_site = True), mostra o site
    - Caso contrário, mostra a página inicial
    """
    # Se for um site válido, redireciona para a view do site
    if getattr(request, "is_site", False) and getattr(request, "tenant", None):
        try:
            from apps.landings.views import site_view

            return site_view(request)
        except Exception as e:
            # Se houver erro ao carregar o site, mostra página inicial
            # Isso pode acontecer se o banco foi resetado e não há dados
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao carregar site: {e}")
            return home(request)

    # Caso contrário, mostra a página inicial
    return home(request)


@login_required
def toggle_theme(request: HttpRequest) -> HttpResponse:
    """
    Alterna o tema do usuário entre claro e escuro.

    Args:
        request: Requisição HTTP

    Returns:
        Redirecionamento para a página anterior
    """
    user = request.user

    # Alterna entre light e dark
    if user.theme_preference == "dark":
        user.theme_preference = "light"
    else:
        user.theme_preference = "dark"

    user.save(update_fields=["theme_preference"])

    # Redireciona de volta para a página anterior
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
@require_http_methods(["GET", "POST"])
def profile(request: HttpRequest) -> HttpResponse:
    """Edição do perfil do usuário."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Perfil atualizado com sucesso."))
            return redirect("core:profile")
    else:
        form = UserProfileForm(instance=request.user)

    context: dict[str, Any] = {
        "form": form,
    }

    return render(request, "core/profile.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def profile_password(request: HttpRequest) -> HttpResponse:
    """Alteração de senha do usuário."""
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantém o usuário logado
            messages.success(request, _("Senha alterada com sucesso."))
            return redirect("core:profile")
    else:
        form = UserPasswordChangeForm(request.user)

    context: dict[str, Any] = {
        "form": form,
    }

    return render(request, "core/profile_password.html", context)


@login_required
@require_POST
def dismiss_onboarding_completion(request: HttpRequest) -> JsonResponse:
    """
    View para dispensar a mensagem de conclusão do onboarding.
    Salva no banco de dados que o usuário fechou a mensagem.
    """
    try:
        onboarding_status = OnboardingStatus.get_or_create_for_user(request.user)
        onboarding_status.dismiss_completion_message()

        return JsonResponse(
            {
                "success": True,
                "message": _("Mensagem de conclusão dispensada com sucesso."),
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": _("Erro ao dispensar mensagem de conclusão."),
                "error": str(e),
            },
            status=400,
        )
