"""
Views do app Landings.

Inclui:
- View pública da landing page (baseada em tenant)
- Views do dashboard para configuração
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from .models import LandingPage, LandingPageTheme


@require_http_methods(["GET"])
def landing_page_view(request):
    """
    View que serve a landing page do tenant detectado pelo middleware.

    Esta view é chamada apenas quando request.is_landing_page = True,
    ou seja, quando o domínio/subdomínio corresponde a uma landing page.
    """
    # Se não for uma requisição de landing page, retorna 404
    if not getattr(request, "is_landing_page", False) or not getattr(request, "tenant", None):
        raise Http404(_("Landing page não encontrada"))

    landing_page = request.tenant

    # Busca os imóveis ativos (com prefetch para otimizar queries)
    properties = landing_page.properties.filter(is_active=True).prefetch_related("images")

    # Imóveis em destaque (máximo 6)
    featured_properties = properties.filter(is_featured=True)[:6]

    # Template a ser usado (do tema selecionado)
    template_path = "landings/themes/default/index.html"  # Fallback
    if landing_page.theme:
        template_path = landing_page.theme.get_template_path("index.html")

    context = {
        "landing_page": landing_page,
        "properties": properties,
        "featured_properties": featured_properties,
        "theme": landing_page.theme,
    }

    return render(request, template_path, context)


@login_required
@require_http_methods(["GET"])
def dashboard_home(request):
    """
    Home do dashboard - mostra visão geral da landing page do usuário.
    """
    # Busca ou cria a landing page do usuário
    try:
        landing_page = LandingPage.objects.select_related("theme").get(owner=request.user)
        properties_count = landing_page.properties.filter(is_active=True).count()
    except LandingPage.DoesNotExist:
        landing_page = None
        properties_count = 0

    context = {
        "landing_page": landing_page,
        "properties_count": properties_count,
    }

    return render(request, "landings/dashboard/home.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_config(request):
    """
    Painel de configuração da landing page do usuário.
    """
    # Busca ou cria a landing page do usuário
    landing_page, created = LandingPage.objects.get_or_create(
        owner=request.user,
        defaults={
            "subdomain": request.user.email.split("@")[0].lower().replace(".", "")[:50],
            "business_name": request.user.get_full_name() or request.user.email,
            "email": request.user.email,
        },
    )

    if created:
        messages.success(request, _("Landing page criada com sucesso! Configure os dados abaixo."))

    # Lista de temas disponíveis
    themes = LandingPageTheme.objects.filter(is_active=True).order_by("order", "name")

    context = {
        "landing_page": landing_page,
        "themes": themes,
    }

    return render(request, "landings/dashboard/config.html", context)


@login_required
@require_http_methods(["GET"])
def dashboard_theme_preview(request, theme_slug):
    """
    Preview de um tema específico.
    """
    theme = get_object_or_404(LandingPageTheme, slug=theme_slug, is_active=True)

    # Busca a landing page do usuário para pré-visualizar com seus dados
    try:
        landing_page = LandingPage.objects.select_related("theme").get(owner=request.user)
    except LandingPage.DoesNotExist:
        messages.warning(request, _("Crie sua landing page primeiro para visualizar o tema."))
        return redirect("landings:dashboard_config")

    # Usa o tema selecionado temporariamente para preview
    properties = landing_page.properties.filter(is_active=True).prefetch_related("images")
    featured_properties = properties.filter(is_featured=True)[:6]

    template_path = theme.get_template_path("index.html")

    context = {
        "landing_page": landing_page,
        "properties": properties,
        "featured_properties": featured_properties,
        "theme": theme,
        "is_preview": True,  # Flag para indicar que é preview
    }

    return render(request, template_path, context)
