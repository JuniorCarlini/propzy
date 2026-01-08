"""
Views do app Administration - Gestão administrativa do sistema
"""

from typing import Any, cast

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.administration.forms import GroupForm, UserCreateForm, UserUpdateForm
from apps.core.permissions import format_permission_label, is_displayable_permission

User = get_user_model()


@login_required
def dashboard(request):
    """Dashboard administrativo com estatísticas do sistema"""
    # Estatísticas básicas
    total_users = User.objects.filter(is_active=True).count() if request.user.has_perm("core.view_user") else 0
    total_groups = Group.objects.count() if request.user.has_perm("auth.view_group") else 0

    # Importar aqui para evitar circular import
    try:
        from apps.landings.models import Site
        from apps.properties.models import Property

        total_sites = Site.objects.count()
        total_properties = Property.objects.count()

        # Buscar site do usuário atual para exibir informações
        try:
            user_site = Site.objects.select_related("theme").get(owner=request.user)
            properties_count = user_site.properties.filter(is_active=True).count()
        except Site.DoesNotExist:
            user_site = None
            properties_count = 0
    except ImportError:
        total_sites = 0
        total_properties = 0
        user_site = None
        properties_count = 0

    context = {
        "total_users": total_users,
        "total_groups": total_groups,
        "total_sites": total_sites,
        "total_properties": total_properties,
        "site": user_site,
        "properties_count": properties_count,
    }

    return render(request, "administration/dashboard.html", context)


@permission_required("core.view_user", raise_exception=True)
def user_list(request):
    """Listagem de usuários cadastrados com busca e paginação."""
    search_query = request.GET.get("q", "").strip()
    users = User.objects.prefetch_related("groups").order_by("email")

    if search_query:
        query = Q(email__icontains=search_query)  # type: ignore[assignment]
        query |= Q(full_name__icontains=search_query)  # type: ignore[operator]
        query |= Q(phone__icontains=search_query)  # type: ignore[operator]
        users = users.filter(query)

    # Paginação
    paginator = Paginator(users, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
    }
    return render(request, "administration/user_list.html", context)


@permission_required("core.add_user", raise_exception=True)
def user_create(request):
    """Criação de usuários com controle de grupos."""
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Usuário criado com sucesso."))
            return redirect("administration:user_list")
    else:
        form = UserCreateForm()

    return render(request, "administration/user_form.html", {"form": form, "title": _("Criar usuário")})


@permission_required("core.change_user", raise_exception=True)
def user_update(request, pk):
    """Atualiza os dados de um usuário existente."""
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Usuário atualizado com sucesso."))
            return redirect("administration:user_list")
    else:
        form = UserUpdateForm(instance=user)

    return render(
        request,
        "administration/user_form.html",
        {
            "form": form,
            "title": _("Editar usuário"),
            "object": user,
        },
    )


@permission_required("core.delete_user", raise_exception=True)
def user_delete(request, pk):
    """Exclui um usuário após confirmação."""
    user = get_object_or_404(User, pk=pk)
    if request.user.pk == user.pk:
        messages.error(request, _("Você não pode remover a si mesmo."))
        return redirect("administration:user_list")
    if request.method == "POST":
        user.delete()
        messages.success(request, _("Usuário removido com sucesso."))
        return redirect("administration:user_list")

    return render(request, "administration/user_confirm_delete.html", {"user": user})


@permission_required("auth.view_group", raise_exception=True)
def group_list(request):
    """Listagem de grupos de permissões."""
    search_query = request.GET.get("q", "").strip()
    groups = Group.objects.prefetch_related("permissions__content_type").order_by("name")

    # Aplicar filtro de busca
    if search_query:
        groups = groups.filter(Q(name__icontains=search_query))

    # Paginação
    paginator = Paginator(groups, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for group in page_obj:
        group_with_attrs = cast(Any, group)
        group_with_attrs.formatted_permissions = [
            format_permission_label(permission)
            for permission in group.permissions.all()
            if is_displayable_permission(permission)
        ]
    return render(request, "administration/group_list.html", {"page_obj": page_obj, "search_query": search_query})


@permission_required("auth.add_group", raise_exception=True)
def group_create(request):
    """Criação de grupos com múltiplas permissões."""
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Grupo criado com sucesso."))
            return redirect("administration:group_list")
    else:
        form = GroupForm()

    return render(request, "administration/group_form.html", {"form": form, "title": _("Criar grupo")})


@permission_required("auth.change_group", raise_exception=True)
def group_update(request, pk):
    """Atualiza um grupo existente e suas permissões."""
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, _("Grupo atualizado com sucesso."))
            return redirect("administration:group_list")
    else:
        form = GroupForm(instance=group)

    return render(
        request,
        "administration/group_form.html",
        {
            "form": form,
            "title": _("Editar grupo"),
        },
    )


@permission_required("auth.delete_group", raise_exception=True)
def group_delete(request, pk):
    """Exclui um grupo de permissões."""
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        group.delete()
        messages.success(request, _("Grupo removido com sucesso."))
        return redirect("administration:group_list")

    return render(request, "administration/group_confirm_delete.html", {"group": group})
