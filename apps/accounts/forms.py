from collections import OrderedDict
from typing import cast

from allauth.account.forms import (
    LoginForm as AllauthLoginForm,
)
from allauth.account.forms import (
    ResetPasswordForm as AllauthResetPasswordForm,
)
from allauth.account.forms import (
    ResetPasswordKeyForm as AllauthResetPasswordKeyForm,
)
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _

from apps.accounts.permissions import (
    DISPLAYABLE_PERMISSION_APPS,
    format_permission_label,
    get_permission_group_label,
)

User = get_user_model()


class AdminUserCreationForm(UserCreationForm):
    """Formulário usado ao criar usuários pelo Django admin."""

    class Meta:
        """Metadados do formulário de criação de usuário."""

        model = User
        fields = (
            "email",
            "full_name",
            "phone",
            "address",
            "city",
            "state",
        )


class AdminUserChangeForm(UserChangeForm):
    """Formulário usado ao atualizar usuários pelo Django admin."""

    class Meta:
        """Metadados do formulário de edição de usuário."""

        model = User
        fields = (
            "email",
            "full_name",
            "phone",
            "address",
            "city",
            "state",
        )


class LoginForm(AllauthLoginForm):
    """Aplica o layout Bootstrap aos campos do formulário de login."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields["login"].widget.attrs.setdefault("class", "form-control")
        self.fields["password"].widget.attrs.setdefault("class", "form-control")
        self.fields["login"].label = _("E-mail")
        self.fields["password"].label = _("Senha")
        if "remember" in self.fields:
            self.fields["remember"].widget.attrs.setdefault("class", "form-check-input")
            self.fields["remember"].label = _("Lembrar acesso")


class ResetPasswordForm(AllauthResetPasswordForm):
    """Aplica o estilo Bootstrap ao formulário de recuperação de senha."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields["email"].widget.attrs.setdefault("class", "form-control")
        self.fields["email"].label = _("E-mail")


class ResetPasswordKeyForm(AllauthResetPasswordKeyForm):
    """Aplica o estilo Bootstrap ao formulário de redefinição definitiva."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields["password1"].widget.attrs.setdefault("class", "form-control")
        self.fields["password2"].widget.attrs.setdefault("class", "form-control")
        self.fields["password1"].label = _("Nova senha")
        self.fields["password2"].label = _("Confirme a nova senha")


class UserCreateForm(UserCreationForm):
    """Formulário para criação de usuários no painel interno."""

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.order_by("name"),
        required=False,
        label=_("Grupos"),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )

    class Meta:
        """Metadados do formulário de criação de usuário."""

        model = User
        fields = (
            "email",
            "full_name",
            "phone",
            "address",
            "city",
            "state",
            "is_active",
            "groups",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        for field_name in (
            "email",
            "full_name",
            "phone",
            "address",
            "city",
            "state",
            "password1",
            "password2",
        ):
            self.fields[field_name].widget.attrs.setdefault("class", "form-control")
        for field_name in ("is_active",):
            self.fields[field_name].widget.attrs.setdefault("class", "form-check-input")
        self.fields["email"].label = _("E-mail")
        self.fields["full_name"].label = _("Nome completo")
        self.fields["phone"].label = _("Telefone")
        self.fields["address"].label = _("Endereço")
        self.fields["city"].label = _("Cidade")
        self.fields["state"].label = _("Estado")
        self.fields["is_active"].label = _("Ativo")
        self.fields["password1"].label = _("Senha")
        self.fields["password2"].label = _("Confirme a senha")
        self.fields["phone"].widget.attrs.update(
            {
                "placeholder": "(00) 00000-0000",
                "inputmode": "tel",
                "data-phone-mask": "true",
                "maxlength": "16",
            }
        )

    def save(self, commit: bool = True) -> AbstractBaseUser:
        user = super().save(commit=False)
        if commit:
            user.save()
        if user.pk:
            groups = self.cleaned_data.get("groups") or []
            user.groups.set(groups)
        return user


class UserUpdateForm(forms.ModelForm):
    """Formulário para edição de usuários no painel interno."""

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.order_by("name"),
        required=False,
        label=_("Grupos"),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )

    class Meta:
        """Metadados do formulário de edição de usuário."""

        model = User
        fields = (
            "email",
            "full_name",
            "phone",
            "address",
            "city",
            "state",
            "is_active",
            "groups",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        for field_name in ("email", "full_name", "phone", "address", "city", "state"):
            self.fields[field_name].widget.attrs.setdefault("class", "form-control")
        for field_name in ("is_active",):
            self.fields[field_name].widget.attrs.setdefault("class", "form-check-input")
        self.fields["email"].label = _("E-mail")
        self.fields["full_name"].label = _("Nome completo")
        self.fields["phone"].label = _("Telefone")
        self.fields["address"].label = _("Endereço")
        self.fields["city"].label = _("Cidade")
        self.fields["state"].label = _("Estado")
        self.fields["is_active"].label = _("Ativo")
        self.fields["phone"].widget.attrs.update(
            {
                "placeholder": "(00) 00000-0000",
                "inputmode": "tel",
                "data-phone-mask": "true",
                "maxlength": "16",
            }
        )

    def save(self, commit: bool = True) -> AbstractBaseUser:
        user = super().save(commit)
        groups = self.cleaned_data.get("groups") or []
        user.groups.set(groups)
        return user


class GroupForm(forms.ModelForm):
    """Formulário para manutenção de grupos de permissões."""

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        label=_("Permissões"),
        help_text=_("Selecione apenas as ações disponíveis para os usuários do sistema."),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check"}),
    )

    class Meta:
        """Metadados do formulário de grupo de permissões."""

        model = Group
        fields = ("name", "permissions")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields["name"].widget.attrs.setdefault("class", "form-control")
        self.fields["name"].label = _("Nome do grupo")
        permissions_field = cast(forms.ModelMultipleChoiceField, self.fields["permissions"])
        filtered_permissions = (
            Permission.objects.select_related("content_type")
            .filter(content_type__app_label__in=DISPLAYABLE_PERMISSION_APPS)
            .order_by("content_type__app_label", "name")
        )
        permissions_field.queryset = filtered_permissions

        grouped_permissions: OrderedDict[str, list[tuple[int, str]]] = OrderedDict()
        for perm in filtered_permissions:
            app_label = perm.content_type.app_label
            group_label = get_permission_group_label(app_label)
            action_label = format_permission_label(perm)
            grouped_permissions.setdefault(group_label, []).append((perm.pk, action_label))

        permissions_field.choices = list(grouped_permissions.items())
        permissions_field.label = _("Permissões disponíveis")
