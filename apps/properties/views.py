"""
Views do app Properties - CRUD de imóveis para o dashboard do corretor
"""

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods, require_POST

from apps.landings.models import Site

from .forms import PropertyForm
from .models import Property, PropertyImage


@login_required
@require_http_methods(["GET"])
def property_list(request):
    """Lista de imóveis do usuário logado."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro para gerenciar imóveis."))
        return redirect("landings:dashboard_config")

    search_query = request.GET.get("q", "").strip()
    property_type_filter = request.GET.get("type", "")
    transaction_filter = request.GET.get("transaction", "")
    status_filter = request.GET.get("status", "")

    properties = Property.objects.filter(site=site).order_by("order", "-created_at")

    # Filtros
    if search_query:
        query = (
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(address__icontains=search_query)
        )
        properties = properties.filter(query)

    if property_type_filter:
        properties = properties.filter(property_type=property_type_filter)

    if transaction_filter:
        properties = properties.filter(transaction_type=transaction_filter)

    if status_filter == "active":
        properties = properties.filter(is_active=True)
    elif status_filter == "inactive":
        properties = properties.filter(is_active=False)
    elif status_filter == "featured":
        properties = properties.filter(is_featured=True)

    # Paginação
    paginator = Paginator(properties, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context: dict[str, Any] = {
        "page_obj": page_obj,
        "search_query": search_query,
        "property_type_filter": property_type_filter,
        "transaction_filter": transaction_filter,
        "status_filter": status_filter,
        "property_types": Property.PROPERTY_TYPES,
        "transaction_types": Property.TRANSACTION_TYPES,
    }

    return render(request, "properties/property_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def property_create(request):
    """Criação de novo imóvel."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro para gerenciar imóveis."))
        return redirect("landings:dashboard_config")

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.site = site
            property_obj.save()

            # Se for requisição AJAX (para upload de imagens), retorna JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    "success": True,
                    "property_id": property_obj.pk,
                    "message": _("Imóvel criado com sucesso.")
                })

            messages.success(request, _("Imóvel criado com sucesso. Adicione imagens abaixo."))
            # Redireciona para a página de edição para permitir adicionar imagens imediatamente
            return redirect("properties:property_update", pk=property_obj.pk)
    else:
        form = PropertyForm(user=request.user)

    context: dict[str, Any] = {
        "form": form,
        "title": _("Criar Imóvel"),
        # Não passa object na criação, mas o template já trata isso
    }

    return render(request, "properties/property_form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def property_update(request, pk):
    """Edição de imóvel existente."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro para gerenciar imóveis."))
        return redirect("landings:dashboard_config")

    property_obj = get_object_or_404(Property, pk=pk, site=site)

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Imóvel atualizado com sucesso."))
            return redirect("properties:property_list")
    else:
        form = PropertyForm(instance=property_obj, user=request.user)

    context: dict[str, Any] = {
        "form": form,
        "title": _("Editar Imóvel"),
        "object": property_obj,
    }

    return render(request, "properties/property_form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def property_toggle_active(request, pk):
    """Ativa ou desativa um imóvel."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro para gerenciar imóveis."))
        return redirect("landings:dashboard_config")

    property_obj = get_object_or_404(Property, pk=pk, site=site)

    if request.method == "POST":
        property_obj.is_active = not property_obj.is_active
        property_obj.save(update_fields=["is_active"])
        if property_obj.is_active:
            messages.success(request, _("Imóvel ativado com sucesso."))
        else:
            messages.success(request, _("Imóvel desativado com sucesso."))
        return redirect("properties:property_list")

    # Se GET, mostra confirmação
    context: dict[str, Any] = {
        "property": property_obj,
    }

    return render(request, "properties/property_toggle_active.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def property_delete(request, pk):
    """Exclusão de um imóvel."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Site não encontrado."))
        return redirect("landings:dashboard_config")

    property_obj = get_object_or_404(Property, pk=pk, site=site)

    if request.method == "POST":
        property_obj.delete()
        messages.success(request, _("Imóvel excluído com sucesso."))
        return redirect("properties:property_list")

    # Se GET, mostra confirmação
    context: dict[str, Any] = {
        "property": property_obj,
    }

    return render(request, "properties/property_delete.html", context)


@login_required
@require_http_methods(["GET"])
def property_detail(request, pk):
    """Detalhes de um imóvel."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        messages.warning(request, _("Crie seu site primeiro para gerenciar imóveis."))
        return redirect("landings:dashboard_config")

    property_obj = get_object_or_404(Property, pk=pk, site=site)

    # Busca imagens adicionais
    images = property_obj.images.all().order_by("order", "created_at")

    context: dict[str, Any] = {
        "property": property_obj,
        "images": images,
    }

    return render(request, "properties/property_detail.html", context)


@login_required
@require_POST
def property_image_upload(request, pk):
    """Upload de imagens para um imóvel via AJAX."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        return JsonResponse({"error": _("Site não encontrado.")}, status=404)

    property_obj = get_object_or_404(Property, pk=pk, site=site)

    # FilePond pode enviar o arquivo com diferentes nomes, tenta encontrar
    uploaded_file = None
    for key in request.FILES:
        uploaded_file = request.FILES[key]
        break

    if not uploaded_file:
        return JsonResponse({"error": _("Nenhum arquivo enviado.")}, status=400)

    # Validação básica do tipo de arquivo
    if not uploaded_file.content_type.startswith("image/"):
        return JsonResponse({"error": _("Apenas arquivos de imagem são permitidos.")}, status=400)

    # Validação do tamanho (máximo 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        return JsonResponse({"error": _("Arquivo muito grande. Tamanho máximo: 10MB.")}, status=400)

    try:
        # Cria a imagem do imóvel
        # Determina a ordem (última ordem + 1)
        last_order = property_obj.images.aggregate(max_order=Max("order"))["max_order"] or 0

        property_image = PropertyImage.objects.create(
            property=property_obj,
            image=uploaded_file,
            order=last_order + 1,
        )

        # Se não houver imagem principal definida, define esta como principal
        is_main = False
        if not property_obj.main_image:
            property_obj.main_image = property_image.image
            property_obj.save(update_fields=["main_image"])
            is_main = True
        else:
            # Verifica se esta imagem já é a principal
            is_main = property_obj.main_image.name == property_image.image.name

        return JsonResponse(
            {
                "success": True,
                "id": property_image.id,
                "url": property_image.image.url,
                "thumbnail": property_image.image.url,
                "order": property_image.order,
                "is_main": is_main,
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def property_image_delete(request, pk, image_id):
    """Exclusão de uma imagem de um imóvel via AJAX."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        return JsonResponse({"error": _("Site não encontrado.")}, status=404)

    property_obj = get_object_or_404(Property, pk=pk, site=site)
    property_image = get_object_or_404(PropertyImage, pk=image_id, property=property_obj)

    try:
        # Verifica se é a imagem principal antes de deletar
        is_main = property_obj.main_image and property_obj.main_image.name == property_image.image.name

        # Deleta o arquivo físico antes de deletar do banco
        if property_image.image:
            property_image.image.delete(save=False)
        property_image.delete()

        # Se a imagem deletada era a principal, define a primeira imagem restante como principal
        if is_main:
            first_image = property_obj.images.first()
            if first_image:
                property_obj.main_image = first_image.image
                property_obj.save(update_fields=["main_image"])
            else:
                # Se não há mais imagens, remove a referência da imagem principal
                property_obj.main_image = None
                property_obj.save(update_fields=["main_image"])

        return JsonResponse({"success": True}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def property_images_list(request, pk):
    """Lista todas as imagens de um imóvel via AJAX."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        return JsonResponse({"error": _("Site não encontrado.")}, status=404)

    property_obj = get_object_or_404(Property, pk=pk, site=site)

    images = property_obj.images.all().order_by("order", "created_at")

    # Verifica qual imagem é a principal comparando o objeto da imagem
    main_image = property_obj.main_image

    images_data = [
        {
            "id": img.id,
            "url": img.image.url,
            "thumbnail": img.image.url,
            "caption": img.caption,
            "order": img.order,
            "is_main": main_image and img.image.name == main_image.name,
        }
        for img in images
    ]

    return JsonResponse({"images": images_data}, status=200)


@login_required
@require_POST
def property_set_main_image(request, pk, image_id):
    """Define uma imagem como principal do imóvel via AJAX."""
    # Busca o site do usuário
    try:
        site = Site.objects.get(owner=request.user)
    except Site.DoesNotExist:
        return JsonResponse({"error": _("Site não encontrado.")}, status=404)

    property_obj = get_object_or_404(Property, pk=pk, site=site)
    property_image = get_object_or_404(PropertyImage, pk=image_id, property=property_obj)

    try:
        # Define a imagem como principal
        property_obj.main_image = property_image.image
        property_obj.save(update_fields=["main_image"])

        return JsonResponse(
            {
                "success": True,
                "message": _("Imagem definida como principal com sucesso."),
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
