"""
Forms do app Properties - Gestão de imóveis
"""

from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Property, PropertyImage


class PropertyForm(forms.ModelForm):
    """Formulário para criação e edição de imóveis."""

    class Meta:
        model = Property
        fields = (
            "title",
            "description",
            "property_type",
            "category",
            "transaction_type",
            "sale_price",
            "rent_price",
            "bedrooms",
            "bathrooms",
            "garage_spaces",
            "area",
            "address",
            "neighborhood",
            "city",
            "state",
            "zipcode",
            # main_image removido - será definido automaticamente via estrela nas imagens adicionais
            "is_featured",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS
        for field_name in (
            "title",
            "description",
            "property_type",
            "category",
            "transaction_type",
            "sale_price",
            "rent_price",
            "bedrooms",
            "bathrooms",
            "garage_spaces",
            "area",
            "address",
            "neighborhood",
            "city",
            "state",
            "zipcode",
        ):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(
                    {
                        "class": "form-control",
                        "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    }
                )

        # Labels traduzidos
        self.fields["title"].label = _("Título")
        self.fields["description"].label = _("Descrição")
        self.fields["property_type"].label = _("Tipo de Imóvel")
        self.fields["category"].label = _("Categoria")
        self.fields["transaction_type"].label = _("Tipo de Transação")
        self.fields["sale_price"].label = _("Preço de Venda")
        self.fields["rent_price"].label = _("Preço de Aluguel")
        self.fields["bedrooms"].label = _("Quartos")
        self.fields["bathrooms"].label = _("Banheiros")
        self.fields["garage_spaces"].label = _("Vagas de Garagem")
        self.fields["area"].label = _("Área (m²)")
        self.fields["address"].label = _("Endereço")
        self.fields["neighborhood"].label = _("Bairro")
        self.fields["city"].label = _("Cidade")
        self.fields["state"].label = _("Estado")
        self.fields["zipcode"].label = _("CEP")
        # main_image removido - será definido automaticamente via estrela nas imagens adicionais
        self.fields["is_featured"].label = _("Destaque")
        self.fields["is_active"].label = _("Ativo")

        # Help texts
        self.fields["description"].widget.attrs.update({"rows": 4})
        self.fields["zipcode"].widget.attrs.update(
            {
                "placeholder": "00000-000",
                "maxlength": "10",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("transaction_type")
        sale_price = cleaned_data.get("sale_price")
        rent_price = cleaned_data.get("rent_price")

        if transaction_type == "sale" and not sale_price:
            raise forms.ValidationError(_("Preço de venda é obrigatório para imóveis à venda."))

        if transaction_type == "rent" and not rent_price:
            raise forms.ValidationError(_("Preço de aluguel é obrigatório para imóveis para alugar."))

        if transaction_type == "both" and not sale_price and not rent_price:
            raise forms.ValidationError(_("Informe pelo menos um preço (venda ou aluguel)."))

        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    """Formulário para adicionar imagens ao imóvel."""

    class Meta:
        model = PropertyImage
        fields = ("image", "caption", "order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        for field_name in ("caption", "order"):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(
                    {
                        "class": "form-control",
                        "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    }
                )

        if "image" in self.fields:
            self.fields["image"].widget.attrs.update(
                {
                    "class": "form-control",
                    "accept": "image/*",
                }
            )

        self.fields["image"].label = _("Imagem")
        self.fields["caption"].label = _("Legenda")
        self.fields["order"].label = _("Ordem")
