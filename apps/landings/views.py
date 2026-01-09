"""
Views do app Landings.

Inclui:
- View pública do site (baseada em tenant)
- Views do dashboard para configuração
"""

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from apps.properties.models import Property

# ATUALIZADO: Theme movido para apps.themes
from apps.themes.models import Theme

from .forms import SiteAdvancedForm, ThemeSectionConfigForm
from .models import Site, ThemeSectionConfig


@require_http_methods(["GET"])
def site_view(request):
    """
    View que serve o site do tenant detectado pelo middleware.

    Esta view é chamada apenas quando request.is_site = True,
    ou seja, quando o domínio/subdomínio corresponde a um site.
    """
    # Se não for uma requisição de site, retorna 404
    if not getattr(request, "is_site", False) or not getattr(request, "tenant", None):
        raise Http404(_("Site não encontrado"))

    site = request.tenant

    # Busca os imóveis ativos (com prefetch para otimizar queries)
    properties = site.properties.filter(is_active=True).prefetch_related("images")

    # Imóveis em destaque (máximo 6)
    featured_properties = properties.filter(is_featured=True)[:6]

    # Buscar configuração da seção de propriedades se existir
    properties_section_config = {}
    try:
        theme_config = site.theme_config
        properties_section_config = theme_config.get_section_config("properties")
    except ThemeSectionConfig.DoesNotExist:
        pass

    # Aplicar filtros da seção de propriedades se configurados
    if properties_section_config.get("enabled", True):
        if properties_section_config.get("show_featured_only"):
            properties = properties.filter(is_featured=True)

        if properties_section_config.get("filter_transaction"):
            transaction = properties_section_config["filter_transaction"]
            if transaction in ["sale", "rent"]:
                properties = properties.filter(transaction_type=transaction)

        if properties_section_config.get("filter_type"):
            properties = properties.filter(property_type=properties_section_config["filter_type"])

        if properties_section_config.get("filter_city"):
            properties = properties.filter(city__icontains=properties_section_config["filter_city"])

        # Aplicar limite
        limit = properties_section_config.get("limit", 0)
        if limit and limit > 0:
            properties = properties[:limit]

    # Template a ser usado (do tema selecionado)
    template_path = "landings/themes/default/index.html"  # Fallback
    if site.theme:
        template_path = site.theme.get_template_path("index.html")

    context = {
        "site": site,
        "properties": properties,
        "featured_properties": featured_properties,
        "theme": site.theme,
        "properties_section_config": properties_section_config,
    }

    return render(request, template_path, context)


@login_required
@require_http_methods(["GET"])
def dashboard_home(request):
    """
    Home do dashboard - redireciona para o dashboard administrativo.
    """
    return redirect("administration_panel:dashboard")


@login_required
@require_http_methods(["GET"])
def check_subdomain_availability(request):
    """
    View AJAX para verificar se o subdomínio gerado a partir do nome do negócio está disponível.
    """
    from django.http import JsonResponse

    business_name = request.GET.get("business_name", "").strip()

    if not business_name:
        return JsonResponse(
            {
                "available": False,
                "message": _("Nome do negócio não pode estar vazio."),
                "subdomain": None,
            }
        )

    # Gerar subdomínio a partir do nome
    generated_subdomain = Site.generate_subdomain_from_business_name(business_name)

    # Verificar se já existe (excluindo o próprio site do usuário se existir)
    try:
        user_site = Site.objects.get(owner=request.user)
        exists = Site.objects.filter(subdomain=generated_subdomain).exclude(pk=user_site.pk).exists()
    except Site.DoesNotExist:
        exists = Site.objects.filter(subdomain=generated_subdomain).exists()

    if exists:
        # Tentar encontrar uma variação disponível
        counter = 1
        suggested_subdomain = None
        while counter <= 10:  # Tentar até 10 variações
            suffix = f"-{counter}"
            max_length = 50 - len(suffix)
            test_subdomain = generated_subdomain[:max_length] + suffix
            try:
                user_site = Site.objects.get(owner=request.user)
                test_exists = Site.objects.filter(subdomain=test_subdomain).exclude(pk=user_site.pk).exists()
            except Site.DoesNotExist:
                test_exists = Site.objects.filter(subdomain=test_subdomain).exists()

            if not test_exists:
                suggested_subdomain = test_subdomain
                break
            counter += 1

        return JsonResponse(
            {
                "available": False,
                "message": _("Este nome geraria o domínio '{subdomain}.propzy.com.br', que já está em uso.").format(
                    subdomain=generated_subdomain
                ),
                "subdomain": generated_subdomain,
                "suggested_subdomain": suggested_subdomain,
                "suggested_message": _("Sugestão: {suggestion}").format(suggestion=suggested_subdomain)
                if suggested_subdomain
                else None,
            }
        )

    return JsonResponse(
        {
            "available": True,
            "message": _("Domínio '{subdomain}.propzy.com.br' está disponível!").format(subdomain=generated_subdomain),
            "subdomain": generated_subdomain,
        }
    )


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_config_basic(request):
    """
    Configurações de dados básicos do site.
    """
    # Busca ou cria o site do usuário
    default_business_name = request.user.get_full_name() or request.user.email
    default_subdomain = Site.generate_subdomain_from_business_name(default_business_name)

    # Verificar se o subdomínio já existe e adicionar sufixo se necessário
    counter = 1
    while Site.objects.filter(subdomain=default_subdomain).exists():
        suffix = f"-{counter}"
        max_length = 50 - len(suffix)
        default_subdomain = Site.generate_subdomain_from_business_name(default_business_name)[:max_length] + suffix
        counter += 1
        if counter > 1000:
            import time

            default_subdomain = f"site-{int(time.time())}"
            break

    site, created = Site.objects.get_or_create(
        owner=request.user,
        defaults={
            "subdomain": default_subdomain,
            "business_name": default_business_name,
            "email": request.user.email,
        },
    )

    if created:
        messages.success(request, _("Site criado com sucesso! Configure os dados abaixo."))

    # Processar formulário
    if request.method == "POST":
        from .forms import SiteBasicForm

        form = SiteBasicForm(request.POST, instance=site)
        if form.is_valid():
            # Salva os valores ANTES de salvar para comparar depois
            old_business_name = site.business_name
            old_subdomain = site.subdomain

            # Salva o formulário - isso atualiza form.instance com os dados salvos
            saved_site = form.save()

            # Usa a instância salva do formulário (já tem os dados atualizados)
            site = saved_site

            # Se o nome do negócio mudou, atualizar o subdomínio
            if old_business_name != site.business_name:
                site.update_subdomain_from_business_name()
                site.save(update_fields=["subdomain"])

                # Informar se a URL mudou
                if old_subdomain != site.subdomain:
                    new_url = site.get_primary_url()
                    messages.success(
                        request,
                        _("Dados básicos salvos com sucesso. A URL do seu site foi atualizada para: {url}").format(
                            url=new_url
                        ),
                    )
                else:
                    messages.success(request, _("Dados básicos salvos com sucesso."))
            else:
                messages.success(request, _("Dados básicos salvos com sucesso."))

            return redirect("landings:dashboard_config_basic")

    # Formulário GET - busca o site novamente do banco para garantir dados atualizados
    # Usa get() em vez de refresh para garantir que pega os dados mais recentes
    site = Site.objects.get(pk=site.pk)
    from .forms import SiteBasicForm

    form = SiteBasicForm(instance=site)

    context = {
        "site": site,
        "form": form,
    }

    return render(request, "landings/dashboard/config_basic.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_config_domain(request):
    """
    Configurações de domínio personalizado do site.
    """
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro."))
        return redirect("landings:dashboard_config_basic")

    # Processar formulário
    if request.method == "POST":
        if "verify_dns" in request.POST:
            # Verificar DNS manualmente
            if site.custom_domain:
                from apps.infrastructure.tasks import check_custom_domain_dns

                result = check_custom_domain_dns.delay(site.pk, site.custom_domain)
                # Aguardar resultado (timeout de 10 segundos)
                try:
                    result_data = result.get(timeout=10)
                    if result_data.get("success"):
                        messages.success(
                            request, _("DNS verificado com sucesso! O domínio está apontado corretamente.")
                        )
                    else:
                        messages.warning(
                            request, _("DNS não configurado ou ainda não propagado. Verifique as configurações.")
                        )
                except Exception:
                    messages.error(request, _("Erro ao verificar DNS. Tente novamente em alguns instantes."))
            else:
                messages.warning(request, _("Configure um domínio personalizado primeiro."))
            return redirect("landings:dashboard_config_domain")

        from .forms import SiteAdvancedForm

        form = SiteAdvancedForm(request.POST, instance=site)
        if form.is_valid():
            old_domain = site.custom_domain
            form.save()

            # Se o domínio mudou, verificar DNS automaticamente
            if form.instance.custom_domain and form.instance.custom_domain != old_domain:
                from apps.infrastructure.tasks import check_custom_domain_dns

                # Verificar DNS após 5 minutos (dar tempo inicial para propagação)
                # A propagação pode levar até 2 horas, então faremos verificações periódicas
                check_custom_domain_dns.apply_async(args=[form.instance.pk, form.instance.custom_domain], countdown=300)

                # Verificações adicionais após 30 minutos, 1 hora e 2 horas
                check_custom_domain_dns.apply_async(
                    args=[form.instance.pk, form.instance.custom_domain], countdown=1800
                )  # 30 min
                check_custom_domain_dns.apply_async(
                    args=[form.instance.pk, form.instance.custom_domain], countdown=3600
                )  # 1 hora
                check_custom_domain_dns.apply_async(
                    args=[form.instance.pk, form.instance.custom_domain], countdown=7200
                )  # 2 horas
                messages.success(
                    request,
                    _(
                        "Configurações de domínio salvas com sucesso. A verificação DNS será feita automaticamente em alguns instantes."
                    ),
                )
            else:
                messages.success(request, _("Configurações de domínio salvas com sucesso."))
            return redirect("landings:dashboard_config_domain")

    # Formulário
    from django.conf import settings

    from .forms import SiteAdvancedForm

    form = SiteAdvancedForm(instance=site)
    base_domain = getattr(settings, "BASE_DOMAIN", "propzy.com.br")

    context = {
        "site": site,
        "form": form,
        "base_domain": base_domain,
    }

    return render(request, "landings/dashboard/config_domain.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_config_theme(request):
    """
    Configurações de temas e layout do site.
    """
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro."))
        return redirect("landings:dashboard_config_domain")

    # Processar formulário
    if request.method == "POST":
        if "apply_theme" in request.POST:
            theme_id = request.POST.get("theme_id")
            try:
                theme = Theme.objects.get(id=theme_id, is_active=True)
                site.theme = theme
                site.save(update_fields=["theme"])
                messages.success(request, _("Tema aplicado com sucesso."))
                return redirect("landings:dashboard_config_theme")
            except Theme.DoesNotExist:
                messages.error(request, _("Tema não encontrado."))
        elif "save_design" in request.POST:
            from .forms import SiteDesignForm

            design = site.get_design()
            design_form = SiteDesignForm(request.POST, instance=design)
            if design_form.is_valid():
                design_form.save()
                messages.success(request, _("Design salvo com sucesso."))
                return redirect("landings:dashboard_config_theme")
        elif "save_section" in request.POST:
            # Processar salvamento de uma seção específica
            section_key = request.POST.get("section_key")
            if section_key:
                # Verificar se é apenas um toggle (vem do toggle da sidebar)
                # O toggle envia apenas: csrf, save_section, section_key e {section_key}_enabled
                enabled_field = f"{section_key}_enabled"
                post_keys = set(request.POST.keys())
                expected_toggle_keys = {"csrfmiddlewaretoken", "save_section", "section_key", enabled_field}

                if enabled_field in request.POST and post_keys == expected_toggle_keys:
                    # É apenas um toggle - salvar apenas o estado enabled
                    theme_config_obj, created = ThemeSectionConfig.objects.get_or_create(
                        site=site, defaults={"sections_config": {}}
                    )
                    existing_config = theme_config_obj.sections_config.get(section_key, {})
                    existing_config["enabled"] = request.POST.get(enabled_field) == "on"
                    sections_config = theme_config_obj.sections_config.copy()
                    sections_config[section_key] = existing_config
                    theme_config_obj.sections_config = sections_config
                    theme_config_obj.save()
                    # Não mostrar mensagem para não poluir a interface
                    return redirect("landings:dashboard_config_theme")

                # É um formulário completo - processar normalmente
                form = ThemeSectionConfigForm(site, section_key, request.POST, request.FILES)
                if form.is_valid():
                    theme_config_obj, created = ThemeSectionConfig.objects.get_or_create(
                        site=site, defaults={"sections_config": {}}
                    )
                    # Buscar configuração existente para preservar o estado enabled
                    existing_config = theme_config_obj.sections_config.get(section_key, {})
                    section_data = {
                        "enabled": existing_config.get("enabled", True),  # Preservar estado do toggle da sidebar
                    }
                    for field_name, value in form.cleaned_data.items():
                        if field_name.startswith(f"{section_key}_"):
                            key = field_name.replace(f"{section_key}_", "")
                            # Não incluir o campo enabled (já foi definido acima)
                            if key != "enabled":
                                section_data[key] = value
                    # Processar upload de imagem se houver
                    image_field_name = (
                        f"{section_key}_background_image" if section_key == "hero" else f"{section_key}_image"
                    )
                    if image_field_name in request.FILES:
                        uploaded_file = request.FILES[image_field_name]
                        # Salvar arquivo
                        from django.core.files.storage import default_storage

                        file_path = default_storage.save(
                            f"themes/sections/{site.id}/{section_key}/{uploaded_file.name}", uploaded_file
                        )
                        section_data["image"] = file_path
                    # Processar campos de serviços (lista de itens)
                    if section_key == "services" and f"{section_key}_items" in form.cleaned_data:
                        items_text = form.cleaned_data[f"{section_key}_items"]
                        if items_text:
                            items_list = [item.strip() for item in items_text.split("\n") if item.strip()]
                            section_data["items"] = items_list
                    sections_config = theme_config_obj.sections_config.copy()
                    sections_config[section_key] = section_data
                    theme_config_obj.sections_config = sections_config
                    theme_config_obj.save()
                    messages.success(request, _("Configuração da seção salva com sucesso."))
                    return redirect("landings:dashboard_config_theme")
        elif "save_sections_order" in request.POST:
            # Processar reordenação de seções
            import json

            try:
                sections_order = json.loads(request.POST.get("sections_order", "[]"))
                theme_config_obj, created = ThemeSectionConfig.objects.get_or_create(
                    site=site, defaults={"sections_config": {}}
                )
                theme_config_obj.sections_order = sections_order
                theme_config_obj.save()
                messages.success(request, _("Ordem das seções salva com sucesso."))
                return redirect("landings:dashboard_config_theme")
            except Exception:
                messages.error(request, _("Erro ao salvar ordem das seções."))

    # Lista de TODOS os temas ordenados:
    # 1. Tema atual do site (se houver)
    # 2. Temas ativos (is_active=True)
    # 3. Temas desabilitados (is_active=False)
    from django.db.models import Case, IntegerField, When

    current_theme_id = site.theme.pk if site.theme else None

    if current_theme_id:
        themes = Theme.objects.annotate(
            display_order=Case(
                When(pk=current_theme_id, then=0),  # Tema atual primeiro
                When(is_active=True, then=1),  # Temas ativos segundo
                When(is_active=False, then=2),  # Temas desabilitados terceiro
                default=3,
                output_field=IntegerField(),
            )
        ).order_by("display_order", "order", "name")
    else:
        # Se não há tema atual, apenas ordena por ativo/desabilitado
        themes = Theme.objects.annotate(
            display_order=Case(
                When(is_active=True, then=1),  # Temas ativos primeiro
                When(is_active=False, then=2),  # Temas desabilitados segundo
                default=3,
                output_field=IntegerField(),
            )
        ).order_by("display_order", "order", "name")
    from .forms import SiteDesignForm

    design = site.get_design()
    design_form = SiteDesignForm(instance=design)

    # Buscar seções disponíveis e configurações
    available_sections = []
    sections_config = {}
    sections_order = []
    first_section_form = None
    first_section_key = None

    if site.theme:
        theme_config = site.theme.get_theme_config()
        available_sections = theme_config.get(
            "sections",
            [
                {
                    "key": "hero",
                    "name": _("Banner Principal"),
                    "icon": "fa-image",
                    "description": _("Banner principal do site"),
                },
                {
                    "key": "about",
                    "name": _("Sobre"),
                    "icon": "fa-user",
                    "description": _("Seção sobre você/empresa"),
                },
                {
                    "key": "services",
                    "name": _("Serviços"),
                    "icon": "fa-briefcase",
                    "description": _("Lista de serviços oferecidos"),
                },
                {
                    "key": "properties",
                    "name": _("Imóveis"),
                    "icon": "fa-home",
                    "description": _("Galeria de imóveis"),
                },
                {
                    "key": "contact",
                    "name": _("Contato"),
                    "icon": "fa-envelope",
                    "description": _("Formulário e informações de contato"),
                },
            ],
        )

        # Buscar configurações existentes
        try:
            theme_config_obj = site.theme_config
            sections_config = theme_config_obj.sections_config
            sections_order = theme_config_obj.sections_order or []
        except ThemeSectionConfig.DoesNotExist:
            sections_config = {}
            sections_order = []

        # Reordenar seções baseado na ordem salva
        if sections_order and len(sections_order) > 0:
            ordered_sections = []
            section_dict = {s["key"]: s for s in available_sections}
            for key in sections_order:
                if key in section_dict:
                    ordered_sections.append(section_dict[key])
            # Adicionar seções que não estão na ordem salva
            for section in available_sections:
                if section["key"] not in sections_order:
                    ordered_sections.append(section)
            available_sections = ordered_sections

        # Criar formulário da primeira seção para exibição inicial
        if available_sections:
            first_section_key = available_sections[0]["key"]
            first_section_form = ThemeSectionConfigForm(site, first_section_key)

    context = {
        "site": site,
        "themes": themes,
        "design_form": design_form,
        "available_sections": available_sections,
        "sections_config": sections_config,
        "sections_order": sections_order,
        "first_section_form": first_section_form,
        "first_section_key": first_section_key,
    }

    return render(request, "landings/dashboard/config_theme.html", context)


@login_required
@require_http_methods(["GET"])
def dashboard_theme_preview(request, theme_slug):
    """
    Preview de um tema específico.
    """
    # ATUALIZADO: Theme movido para apps.themes
    theme = get_object_or_404(Theme, slug=theme_slug, is_active=True)

    # Busca o site do usuário para pré-visualizar com seus dados
    try:
        site = Site.objects.select_related("theme").get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro para visualizar o tema."))
        return redirect("landings:dashboard_config_domain")

    # Usa o tema selecionado temporariamente para preview
    properties = site.properties.filter(is_active=True).prefetch_related("images")
    featured_properties = properties.filter(is_featured=True)[:6]

    template_path = theme.get_template_path("index.html")

    context = {
        "site": site,
        "properties": properties,
        "featured_properties": featured_properties,
        "theme": theme,
        "is_preview": True,  # Flag para indicar que é preview
    }

    return render(request, template_path, context)


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_advanced_config(request):
    """
    Configurações avançadas do site (SEO, cores, etc).
    """
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro."))
        return redirect("landings:dashboard_config_domain")

    if request.method == "POST":
        form = SiteAdvancedForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, _("Configurações avançadas salvas com sucesso."))
            return redirect("landings:dashboard_advanced_config")
    else:
        form = SiteAdvancedForm(instance=site)

    context: dict[str, Any] = {
        "form": form,
        "site": site,
    }

    return render(request, "landings/dashboard/advanced_config.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_theme_sections(request):
    """
    View antiga - redireciona para dashboard_config_theme.
    Mantida para compatibilidade com URLs antigas e bookmarks.
    """
    return redirect("landings:dashboard_config_theme")


@login_required
@require_http_methods(["GET", "POST"])
def dashboard_section_config_form(request, section_key):
    """Retorna o formulário de uma seção específica via HTMX"""
    site = get_object_or_404(Site, owner=request.user)

    # Se for POST, processar salvamento
    if request.method == "POST":
        form = ThemeSectionConfigForm(site, section_key, request.POST, request.FILES)
        if form.is_valid():
            theme_config_obj, created = ThemeSectionConfig.objects.get_or_create(
                site=site, defaults={"sections_config": {}}
            )
            # Buscar configuração existente para preservar o estado enabled
            existing_config = theme_config_obj.sections_config.get(section_key, {})
            section_data = {
                "enabled": existing_config.get("enabled", True),  # Preservar estado do toggle da sidebar
            }
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith(f"{section_key}_"):
                    key = field_name.replace(f"{section_key}_", "")
                    # Não incluir o campo enabled (já foi definido acima)
                    if key != "enabled":
                        section_data[key] = value
            # Processar upload de imagem se houver
            image_field_name = f"{section_key}_background_image" if section_key == "hero" else f"{section_key}_image"
            if image_field_name in request.FILES:
                uploaded_file = request.FILES[image_field_name]
                from django.core.files.storage import default_storage

                file_path = default_storage.save(
                    f"themes/sections/{site.pk}/{section_key}/{uploaded_file.name}", uploaded_file
                )
                section_data["image"] = file_path
            # Processar campos de serviços (lista de itens)
            if section_key == "services" and f"{section_key}_items" in form.cleaned_data:
                items_text = form.cleaned_data[f"{section_key}_items"]
                if items_text:
                    items_list = [item.strip() for item in items_text.split("\n") if item.strip()]
                    section_data["items"] = items_list
            sections_config = theme_config_obj.sections_config.copy()
            sections_config[section_key] = section_data
            theme_config_obj.sections_config = sections_config
            theme_config_obj.save()
            messages.success(request, _("Configuração salva com sucesso."))
    else:
        form = ThemeSectionConfigForm(site, section_key)

    # Buscar imagem salva da seção se existir
    section_image_url = None
    try:
        theme_config_obj = site.theme_config
        section_config = theme_config_obj.get_section_config(section_key)
        image_path = section_config.get("image")
        if image_path:
            from django.core.files.storage import default_storage
            if default_storage.exists(image_path):
                section_image_url = default_storage.url(image_path)
    except (ThemeSectionConfig.DoesNotExist, AttributeError):
        pass

    # Buscar seções disponíveis
    if site.theme:
        theme_config = site.theme.get_theme_config()
        available_sections = theme_config.get("sections", [])
    else:
        available_sections = []

    return render(
        request,
        "landings/dashboard/partials/section_form.html",
        {
            "form": form,
            "section_key": section_key,
            "site": site,
            "available_sections": available_sections,
            "section_image_url": section_image_url,
        },
    )


@require_http_methods(["GET"])
def properties_list(request):
    """
    Página pública para listar todos os imóveis do site.
    Funciona tanto quando acessado diretamente no domínio quanto via /landings/
    """
    # Tenta obter o site do tenant (quando acessado diretamente no domínio)
    site = getattr(request, "tenant", None)

    # Se não houver tenant (acessado via /landings/), tenta usar o site do usuário logado
    if not site and request.user.is_authenticated:
        try:
            site = Site.objects.get(owner=request.user)
        except Site.DoesNotExist:
            pass

    # Se ainda não houver site, retorna 404
    if not site:
        raise Http404(_("Site não encontrado"))

    # Busca os imóveis ativos (com prefetch para otimizar queries)
    # Ordena primeiro por destaque (is_featured), depois por order e data de criação
    properties = (
        site.properties.filter(is_active=True)
        .prefetch_related("images")
        .order_by("-is_featured", "order", "-created_at")
    )

    # Filtros
    property_type_filter = request.GET.get("type", "")
    transaction_filter = request.GET.get("transaction", "")
    city_filter = request.GET.get("city", "")
    search_query = request.GET.get("q", "").strip()

    if search_query:
        from django.db.models import Q

        query = (
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(address__icontains=search_query)
            | Q(neighborhood__icontains=search_query)
        )
        properties = properties.filter(query)

    if property_type_filter:
        properties = properties.filter(property_type=property_type_filter)

    if transaction_filter:
        properties = properties.filter(transaction_type=transaction_filter)

    if city_filter:
        properties = properties.filter(city=city_filter)

    # Lista de cidades para o filtro (antes da paginação)
    all_properties = site.properties.filter(is_active=True)
    cities = all_properties.values_list("city", flat=True).distinct().order_by("city")

    # Paginação
    from django.core.paginator import Paginator

    paginator = Paginator(properties, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Template a ser usado (do tema selecionado)
    template_path = "landings/themes/default/properties_list.html"  # Fallback
    if site.theme:
        template_path = site.theme.get_template_path("properties_list.html")

    context = {
        "site": site,
        "properties": page_obj,
        "cities": cities,
        "property_type_filter": property_type_filter,
        "transaction_filter": transaction_filter,
        "city_filter": city_filter,
        "search_query": search_query,
        "theme": site.theme,
    }

    return render(request, template_path, context)


@require_http_methods(["GET"])
def property_detail(request, pk):
    """
    Página pública para ver detalhes de um imóvel.
    Funciona tanto quando acessado diretamente no domínio quanto via /landings/
    """
    # Tenta obter o site do tenant (quando acessado diretamente no domínio)
    site = getattr(request, "tenant", None)

    # Se não houver tenant (acessado via /landings/), tenta usar o site do usuário logado
    if not site and request.user.is_authenticated:
        try:
            site = Site.objects.get(owner=request.user)
        except Site.DoesNotExist:
            pass

    # Se ainda não houver site, retorna 404
    if not site:
        raise Http404(_("Site não encontrado"))

    # Busca o imóvel (deve pertencer ao site e estar ativo)
    property_obj = get_object_or_404(Property, pk=pk, site=site, is_active=True)

    # Busca imagens adicionais
    images = property_obj.images.all().order_by("order", "created_at")

    # Busca imóveis relacionados (mesmo tipo, mesma cidade, excluindo o atual)
    related_properties = (
        site.properties.filter(is_active=True, property_type=property_obj.property_type, city=property_obj.city)
        .exclude(pk=property_obj.pk)
        .prefetch_related("images")[:4]
    )

    # Template a ser usado (do tema selecionado)
    template_path = "landings/themes/default/property_detail.html"  # Fallback
    if site.theme:
        template_path = site.theme.get_template_path("property_detail.html")

    context: dict[str, Any] = {
        "site": site,
        "property": property_obj,
        "images": images,
        "related_properties": related_properties,
        "theme": site.theme,
    }

    return render(request, template_path, context)
