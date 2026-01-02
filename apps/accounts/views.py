from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import GroupForm, UserCreateForm, UserUpdateForm
from apps.accounts.models import User
from apps.accounts.permissions import format_permission_label, is_displayable_permission


@permission_required("accounts.view_user", raise_exception=True)
def user_list(request):
    """Listagem de usuários cadastrados com busca e paginação."""

    search_query = request.GET.get("q", "").strip()
    users = User.objects.prefetch_related("groups", "department").order_by("email")

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
    return render(request, "accounts/user_list.html", context)


@permission_required("accounts.add_user", raise_exception=True)
def user_create(request):
    """Criação de usuários com controle de grupos."""

    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Usuário criado com sucesso."))
            return redirect("accounts:user_list")
    else:
        form = UserCreateForm()

    return render(request, "accounts/user_form.html", {"form": form, "title": _("Criar usuário")})


@permission_required("accounts.change_user", raise_exception=True)
def user_update(request, pk):
    """Atualiza os dados de um usuário existente."""

    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Usuário atualizado com sucesso."))
            return redirect("accounts:user_list")
    else:
        form = UserUpdateForm(instance=user)

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": _("Editar usuário"),
        },
    )


@permission_required("accounts.delete_user", raise_exception=True)
def user_delete(request, pk):
    """Exclui um usuário após confirmação."""

    user = get_object_or_404(User, pk=pk)
    if request.user.pk == user.pk:
        messages.error(request, _("Você não pode remover a si mesmo."))
        return redirect("accounts:user_list")
    if request.method == "POST":
        user.delete()
        messages.success(request, _("Usuário removido com sucesso."))
        return redirect("accounts:user_list")

    return render(request, "accounts/user_confirm_delete.html", {"user": user})


@permission_required("auth.view_group", raise_exception=True)
def group_list(request):
    """Listagem de grupos de permissões."""

    groups = Group.objects.prefetch_related("permissions__content_type").order_by("name")
    for group in groups:
        group_with_attrs = cast(Any, group)
        group_with_attrs.formatted_permissions = [
            format_permission_label(permission)
            for permission in group.permissions.all()
            if is_displayable_permission(permission)
        ]
    return render(request, "accounts/group_list.html", {"groups": groups})


@permission_required("auth.add_group", raise_exception=True)
def group_create(request):
    """Criação de grupos com múltiplas permissões."""

    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Grupo criado com sucesso."))
            return redirect("accounts:group_list")
    else:
        form = GroupForm()

    return render(request, "accounts/group_form.html", {"form": form, "title": _("Criar grupo")})


@permission_required("auth.change_group", raise_exception=True)
def group_update(request, pk):
    """Atualiza um grupo existente e suas permissões."""

    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, _("Grupo atualizado com sucesso."))
            return redirect("accounts:group_list")
    else:
        form = GroupForm(instance=group)

    return render(
        request,
        "accounts/group_form.html",
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
        return redirect("accounts:group_list")

    return render(request, "accounts/group_confirm_delete.html", {"group": group})
