"""
Forms do app Core - Perfil do usuário e formulários do allauth
"""

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import LoginForm as AllauthLoginForm
from allauth.account.forms import ResetPasswordForm as AllauthResetPasswordForm
from allauth.account.forms import ResetPasswordKeyForm as AllauthResetPasswordKeyForm

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário."""

    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
            "phone",
            "address",
            "city",
            "state",
            "theme_preference",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS
        for field_name in ("email", "full_name", "phone", "address", "city", "state"):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(
                    {
                        "class": "form-control",
                        "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    }
                )

        if "theme_preference" in self.fields:
            self.fields["theme_preference"].widget.attrs.update(
                {
                    "class": "form-select",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            )

        # Labels traduzidos
        self.fields["email"].label = _("E-mail")
        self.fields["full_name"].label = _("Nome completo")
        self.fields["phone"].label = _("Telefone")
        self.fields["address"].label = _("Endereço")
        self.fields["city"].label = _("Cidade")
        self.fields["state"].label = _("Estado")
        self.fields["theme_preference"].label = _("Preferência de Tema")

        # Help texts
        if "phone" in self.fields:
            self.fields["phone"].widget.attrs.update(
                {
                    "placeholder": "(00) 00000-0000",
                    "inputmode": "tel",
                    "data-phone-mask": "true",
                    "maxlength": "16",
                }
            )

        # Email não pode ser alterado
        self.fields["email"].disabled = True
        self.fields["email"].help_text = _("O e-mail não pode ser alterado.")


class UserPasswordChangeForm(PasswordChangeForm):
    """Formulário para alteração de senha."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS
        for field_name in ("old_password", "new_password1", "new_password2"):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(
                    {
                        "class": "form-control",
                        "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    }
                )

        # Labels traduzidos
        self.fields["old_password"].label = _("Senha atual")
        self.fields["new_password1"].label = _("Nova senha")
        self.fields["new_password2"].label = _("Confirmar nova senha")


# Formulários do django-allauth customizados
class LoginForm(AllauthLoginForm):
    """Formulário de login customizado com crispy-forms"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS aos campos
        if "login" in self.fields:
            self.fields["login"].widget.attrs.update(
                {
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    "placeholder": _("Seu e-mail"),
                    "autocomplete": "email",
                }
            )
        if "password" in self.fields:
            self.fields["password"].widget.attrs.update(
                {
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    "placeholder": _("Sua senha"),
                    "autocomplete": "current-password",
                }
            )
        if "remember" in self.fields:
            self.fields["remember"].widget.attrs.update(
                {
                    "class": "form-check-input",
                }
            )

        # Labels traduzidos
        if "login" in self.fields:
            self.fields["login"].label = _("E-mail")
        if "password" in self.fields:
            self.fields["password"].label = _("Senha")
        if "remember" in self.fields:
            self.fields["remember"].label = _("Lembrar acesso")


class ResetPasswordForm(AllauthResetPasswordForm):
    """Formulário de recuperação de senha customizado com crispy-forms"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS
        if "email" in self.fields:
            self.fields["email"].widget.attrs.update(
                {
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    "placeholder": _("seu@email.com"),
                    "autocomplete": "email",
                }
            )
            self.fields["email"].label = _("E-mail")


class ResetPasswordKeyForm(AllauthResetPasswordKeyForm):
    """Formulário de redefinição de senha customizado com crispy-forms"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS
        for field_name in ("password1", "password2"):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(
                    {
                        "class": "form-control",
                        "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                        "autocomplete": "new-password",
                    }
                )

        # Labels traduzidos
        if "password1" in self.fields:
            self.fields["password1"].label = _("Nova senha")
        if "password2" in self.fields:
            self.fields["password2"].label = _("Confirmar nova senha")
