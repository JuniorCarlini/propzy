"""
Forms do app Landings - Configurações do site
"""

from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Site, SiteDesign, ThemeSectionConfig


class SiteBasicForm(forms.ModelForm):
    """Formulário para dados básicos do site (incluindo SEO)."""

    class Meta:
        model = Site
        fields = (
            "business_name",
            "email",
            "phone",
            "whatsapp",
            "address",
            "city",
            "state",
            "meta_title",
            "meta_description",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS
        for field_name in self.fields:
            if field_name in self.fields:
                widget = self.fields[field_name].widget
                # Campos de SEO sempre como textarea
                if field_name in ["meta_title", "meta_description"]:
                    widget = forms.Textarea(
                        attrs={
                            "class": "form-control",
                            "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; min-height: 80px; resize: vertical;",
                            "rows": "3",
                        }
                    )
                    self.fields[field_name].widget = widget
                elif isinstance(widget, forms.Textarea):
                    widget.attrs.update(
                        {
                            "class": "form-control",
                            "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; min-height: 100px; resize: vertical;",
                        }
                    )
                else:
                    widget.attrs.update(
                        {
                            "class": "form-control",
                            "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                        }
                    )

        # Labels traduzidos
        self.fields["business_name"].label = _("Nome do Negócio")
        self.fields["email"].label = _("E-mail de Contato")
        self.fields["phone"].label = _("Telefone")
        self.fields["whatsapp"].label = _("WhatsApp")
        self.fields["address"].label = _("Endereço")
        self.fields["city"].label = _("Cidade")
        self.fields["state"].label = _("Estado")
        self.fields["meta_title"].label = _("Título para Buscas (SEO)")
        self.fields["meta_description"].label = _("Descrição para Buscas (SEO)")

        # Help texts explicativos e claros
        # business_name não tem help_text (explicação está no alerta no topo)
        self.fields["business_name"].help_text = ""
        self.fields["email"].help_text = _("E-mail onde os visitantes do site podem entrar em contato com você.")
        self.fields["phone"].help_text = _("Telefone fixo ou celular para contato (opcional).")
        self.fields["whatsapp"].help_text = _(
            "Número do WhatsApp com DDD (ex: 11987654321). Será usado no botão de contato do site."
        )
        self.fields["address"].help_text = _("Endereço completo do seu negócio (rua, número, complemento).")
        self.fields["city"].help_text = _("Cidade onde seu negócio está localizado.")
        self.fields["state"].help_text = _("Estado onde seu negócio está localizado (ex: SP, RJ, MG).")
        # Help texts dos campos de SEO
        self.fields["meta_title"].help_text = _(
            "Título que aparece nos resultados de busca do Google. Seja objetivo e use palavras-chave importantes. Máximo 60 caracteres."
        )
        self.fields["meta_description"].help_text = _(
            "Descrição curta que aparece abaixo do título nos resultados de busca. Explique brevemente o que seu negócio oferece. Máximo 160 caracteres."
        )

        # Validações para SEO
        self.fields["meta_title"].max_length = 60
        self.fields["meta_description"].max_length = 160

        # Configurar máscara de telefone para phone e whatsapp
        if "phone" in self.fields:
            self.fields["phone"].widget.attrs.update(
                {
                    "placeholder": "(00) 00000-0000",
                    "inputmode": "tel",
                    "data-phone-mask": "true",
                    "maxlength": "16",
                }
            )
            # Formatar valor inicial se existir (vindo do banco sem formatação)
            if self.instance and self.instance.pk and self.instance.phone:
                import re

                phone_digits = re.sub(r"\D", "", self.instance.phone)
                if phone_digits:
                    if len(phone_digits) <= 2:
                        formatted = f"({phone_digits}"
                    elif len(phone_digits) <= 6:
                        formatted = f"({phone_digits[:2]}) {phone_digits[2:]}"
                    elif len(phone_digits) <= 10:
                        formatted = f"({phone_digits[:2]}) {phone_digits[2:6]}-{phone_digits[6:]}"
                    else:
                        formatted = f"({phone_digits[:2]}) {phone_digits[2:7]}-{phone_digits[7:]}"
                    self.initial["phone"] = formatted

        if "whatsapp" in self.fields:
            self.fields["whatsapp"].widget.attrs.update(
                {
                    "placeholder": "(00) 00000-0000",
                    "inputmode": "tel",
                    "data-phone-mask": "true",
                    "maxlength": "16",
                }
            )
            # Formatar valor inicial se existir (vindo do banco sem formatação)
            if self.instance and self.instance.pk and self.instance.whatsapp:
                import re

                whatsapp_digits = re.sub(r"\D", "", self.instance.whatsapp)
                if whatsapp_digits:
                    if len(whatsapp_digits) <= 2:
                        formatted = f"({whatsapp_digits}"
                    elif len(whatsapp_digits) <= 6:
                        formatted = f"({whatsapp_digits[:2]}) {whatsapp_digits[2:]}"
                    elif len(whatsapp_digits) <= 10:
                        formatted = f"({whatsapp_digits[:2]}) {whatsapp_digits[2:6]}-{whatsapp_digits[6:]}"
                    else:
                        formatted = f"({whatsapp_digits[:2]}) {whatsapp_digits[2:7]}-{whatsapp_digits[7:]}"
                    self.initial["whatsapp"] = formatted

    def clean(self):
        """
        Remove formatação dos campos de telefone antes de salvar no banco.
        """
        import re

        cleaned_data = super().clean()

        # Remover formatação de phone e whatsapp (deixar apenas números)
        if "phone" in cleaned_data and cleaned_data["phone"]:
            cleaned_data["phone"] = re.sub(r"\D", "", cleaned_data["phone"])

        if "whatsapp" in cleaned_data and cleaned_data["whatsapp"]:
            cleaned_data["whatsapp"] = re.sub(r"\D", "", cleaned_data["whatsapp"])

        return cleaned_data


class SiteAdvancedForm(forms.ModelForm):
    """Formulário para configurações de domínio personalizado."""

    class Meta:
        model = Site
        fields = ("custom_domain",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS
        if "custom_domain" in self.fields:
            self.fields["custom_domain"].widget.attrs.update(
                {
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            )

        # Labels traduzidos
        self.fields["custom_domain"].label = _("Domínio Personalizado")

        # Help texts
        self.fields["custom_domain"].help_text = _(
            "Domínio personalizado (ex: meusite.com.br). Configure o DNS apontando para nosso servidor."
        )


class SiteDesignForm(forms.ModelForm):
    """Formulário para configurações de design do site."""

    class Meta:
        model = SiteDesign
        fields = (
            "primary_color",
            "secondary_color",
            "tertiary_color",
            "quaternary_color",
            "success_color",
            "danger_color",
            "warning_color",
            "info_color",
            "text_primary_color",
            "text_secondary_color",
            "background_color",
            "border_color",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Aplicar classes CSS e atributo data-coloris para todos os campos de cor
        color_fields = [
            "primary_color",
            "secondary_color",
            "tertiary_color",
            "quaternary_color",
            "success_color",
            "danger_color",
            "warning_color",
            "info_color",
            "text_primary_color",
            "text_secondary_color",
            "background_color",
            "border_color",
        ]

        for field_name in color_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(
                    {
                        "class": "form-control color-input",
                        "data-coloris": "",
                        "style": "flex: 1; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    }
                )

        # Labels traduzidos
        self.fields["primary_color"].label = _("Cor Primária")
        self.fields["secondary_color"].label = _("Cor Secundária")
        self.fields["tertiary_color"].label = _("Cor Terciária")
        self.fields["quaternary_color"].label = _("Cor Quaternária")
        self.fields["success_color"].label = _("Cor de Sucesso")
        self.fields["danger_color"].label = _("Cor de Erro")
        self.fields["warning_color"].label = _("Cor de Aviso")
        self.fields["info_color"].label = _("Cor de Informação")
        self.fields["text_primary_color"].label = _("Cor de Texto Primária")
        self.fields["text_secondary_color"].label = _("Cor de Texto Secundária")
        self.fields["background_color"].label = _("Cor de Fundo")
        self.fields["border_color"].label = _("Cor de Borda")

        # Help texts
        self.fields["primary_color"].help_text = _("Cor principal do tema (botões, links principais)")
        self.fields["secondary_color"].help_text = _("Cor secundária do tema (botões secundários, destaques)")
        self.fields["tertiary_color"].help_text = _("Cor terciária do tema (elementos especiais)")
        self.fields["quaternary_color"].help_text = _("Cor quaternária do tema (destaques alternativos)")
        self.fields["success_color"].help_text = _("Cor para mensagens e elementos de sucesso")
        self.fields["danger_color"].help_text = _("Cor para mensagens e elementos de erro")
        self.fields["warning_color"].help_text = _("Cor para mensagens e elementos de aviso")
        self.fields["info_color"].help_text = _("Cor para mensagens e elementos informativos")
        self.fields["text_primary_color"].help_text = _("Cor principal do texto")
        self.fields["text_secondary_color"].help_text = _("Cor secundária do texto (textos menos importantes)")
        self.fields["background_color"].help_text = _("Cor de fundo principal do site")
        self.fields["border_color"].help_text = _("Cor das bordas e divisórias")

    def clean(self):
        """Valida que todas as cores estão no formato hexadecimal."""
        import re

        cleaned_data = super().clean()

        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")

        for field_name, value in cleaned_data.items():
            if value and not hex_pattern.match(value):
                self.add_error(
                    field_name, forms.ValidationError(_("A cor deve estar no formato hexadecimal (ex: #007bff)"))
                )

        return cleaned_data


class ThemeSectionConfigForm(forms.Form):
    """Formulário dinâmico para configurar seções do tema"""

    def __init__(self, site, section_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site = site
        self.section_key = section_key

        # Buscar configuração existente
        try:
            theme_config = site.theme_config
            section_config = theme_config.get_section_config(section_key)
        except ThemeSectionConfig.DoesNotExist:
            section_config = {}

        # Campos específicos por tipo de seção
        if section_key == "hero":
            self._add_hero_fields(section_config)
        elif section_key == "about":
            self._add_about_fields(section_config)
        elif section_key == "services":
            self._add_services_fields(section_config)
        elif section_key == "contact":
            self._add_contact_fields(section_config)
        elif section_key == "properties":
            self._add_properties_fields(section_config)

    def _add_hero_fields(self, config):
        """Campos para seção Hero"""
        self.fields["hero_enabled"] = forms.BooleanField(
            label=_("Exibir seção Hero"),
            initial=config.get("enabled", True),
            required=False,
        )
        self.fields["hero_title"] = forms.CharField(
            label=_("Título Principal"),
            max_length=200,
            initial=config.get("title", self.site.business_name),
            help_text=_("Título principal exibido no banner"),
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    "placeholder": _("Ex: Encontre o imóvel dos seus sonhos"),
                }
            ),
        )
        self.fields["hero_subtitle"] = forms.CharField(
            label=_("Subtítulo"),
            max_length=500,
            initial=config.get("subtitle", ""),
            required=False,
            help_text=_("Texto descritivo abaixo do título"),
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; min-height: 100px; resize: vertical;",
                    "rows": 3,
                    "placeholder": _("Descreva brevemente seu negócio"),
                }
            ),
        )
        self.fields["hero_background_image"] = forms.ImageField(
            label=_("Imagem de Fundo"),
            required=False,
            help_text=_("Se não selecionar, usará a imagem principal do site"),
        )
        self.fields["hero_text_position"] = forms.ChoiceField(
            label=_("Alinhamento do Conteúdo"),
            choices=[
                ("left", _("Esquerda")),
                ("center", _("Centro")),
                ("right", _("Direita")),
            ],
            initial=config.get("text_position", "left"),
            help_text=_("Alinha o bloco completo (título, subtítulo e botões) na posição escolhida"),
            widget=forms.HiddenInput(),  # Campo oculto, será controlado pelos botões visuais
        )
        self.fields["hero_show_cta"] = forms.BooleanField(
            label=_("Mostrar botões de ação"),
            initial=config.get("show_cta", True),
            required=False,
        )
        self.fields["hero_cta_text"] = forms.CharField(
            label=_("Texto do botão principal"),
            max_length=50,
            initial=config.get("cta_text", _("Ver Imóveis")),
            required=False,
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
        self.fields["hero_cta_url"] = forms.URLField(
            label=_("URL do botão"),
            max_length=500,
            initial=config.get("cta_url", "#imoveis"),
            required=False,
            help_text=_("Link para onde o botão irá redirecionar (ex: #imoveis, /contato, https://exemplo.com)"),
            widget=forms.URLInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    "placeholder": _("Ex: #imoveis ou https://exemplo.com"),
                }
            ),
        )

    def _add_about_fields(self, config):
        """Campos para seção Sobre"""
        self.fields["about_enabled"] = forms.BooleanField(
            label=_("Exibir seção Sobre"),
            initial=config.get("enabled", True),
            required=False,
        )
        self.fields["about_title"] = forms.CharField(
            label=_("Título da Seção"),
            max_length=200,
            initial=config.get("title", _("Sobre mim")),
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
        self.fields["about_description"] = forms.CharField(
            label=_("Descrição"),
            initial=config.get("description", ""),
            required=False,
            help_text=_("Conte sua história, experiência e valores"),
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; min-height: 150px; resize: vertical;",
                    "rows": 6,
                    "placeholder": _("Conte sua história, experiência e valores..."),
                }
            ),
        )
        self.fields["about_image"] = forms.ImageField(
            label=_("Foto/Imagem"),
            required=False,
            help_text=_("Se não selecionar, usará a imagem principal do site"),
        )
        self.fields["about_image_position"] = forms.ChoiceField(
            label=_("Posição da Imagem"),
            choices=[
                ("left", _("Esquerda")),
                ("right", _("Direita")),
            ],
            initial=config.get("image_position", "left"),
            widget=forms.HiddenInput(),  # Campo oculto, será controlado pelos botões visuais
        )

    def _add_services_fields(self, config):
        """Campos para seção Serviços"""
        self.fields["services_enabled"] = forms.BooleanField(
            label=_("Exibir seção Serviços"),
            initial=config.get("enabled", True),
            required=False,
        )
        self.fields["services_title"] = forms.CharField(
            label=_("Título da Seção"),
            max_length=200,
            initial=config.get("title", _("Nossos Serviços")),
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
        self.fields["services_subtitle"] = forms.CharField(
            label=_("Subtítulo"),
            max_length=500,
            initial=config.get("subtitle", ""),
            required=False,
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; min-height: 80px; resize: vertical;",
                    "rows": 2,
                }
            ),
        )
        # Serviços podem ser uma lista
        items = config.get("items", [])
        self.fields["services_items"] = forms.CharField(
            label=_("Itens de Serviços (um por linha)"),
            initial="\n".join(items) if isinstance(items, list) else items,
            required=False,
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; min-height: 120px; resize: vertical;",
                    "rows": 6,
                    "placeholder": _("Ex:\nVenda de Imóveis\nAluguel\nAvaliações\nConsultoria"),
                }
            ),
        )

    def _add_contact_fields(self, config):
        """Campos para seção Contato"""
        self.fields["contact_enabled"] = forms.BooleanField(
            label=_("Exibir seção Contato"),
            initial=config.get("enabled", True),
            required=False,
        )
        self.fields["contact_title"] = forms.CharField(
            label=_("Título da Seção"),
            max_length=200,
            initial=config.get("title", _("Entre em Contato")),
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
        self.fields["contact_show_form"] = forms.BooleanField(
            label=_("Mostrar formulário de contato"),
            initial=config.get("show_form", True),
            required=False,
        )
        self.fields["contact_show_map"] = forms.BooleanField(
            label=_("Mostrar mapa"),
            initial=config.get("show_map", False),
            required=False,
        )

    def _add_properties_fields(self, config):
        """Campos para seção Imóveis"""
        self.fields["properties_enabled"] = forms.BooleanField(
            label=_("Exibir seção Imóveis"),
            initial=config.get("enabled", True),
            required=False,
        )
        self.fields["properties_title"] = forms.CharField(
            label=_("Título da Seção"),
            max_length=200,
            initial=config.get("title", _("Imóveis Disponíveis")),
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
        self.fields["properties_subtitle"] = forms.CharField(
            label=_("Subtítulo (opcional)"),
            max_length=500,
            initial=config.get("subtitle", ""),
            required=False,
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    "placeholder": _("Ex: Encontre o imóvel perfeito para você"),
                }
            ),
        )
        # Filtros simples
        self.fields["properties_filter_transaction"] = forms.ChoiceField(
            label=_("Filtrar por Finalidade"),
            choices=[
                ("", _("Todos")),
                ("sale", _("Venda")),
                ("rent", _("Aluguel")),
                ("both", _("Venda/Aluguel")),
            ],
            initial=config.get("filter_transaction", ""),
            required=False,
            help_text=_("Mostrar apenas imóveis com esta finalidade"),
            widget=forms.Select(
                attrs={
                    "class": "form-select",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
        self.fields["properties_filter_type"] = forms.ChoiceField(
            label=_("Filtrar por Tipo"),
            choices=[
                ("", _("Todos")),
                ("house", _("Casa")),
                ("apartment", _("Apartamento")),
                ("commercial", _("Comercial")),
                ("land", _("Terreno")),
                ("farm", _("Fazenda")),
            ],
            initial=config.get("filter_type", ""),
            required=False,
            help_text=_("Mostrar apenas este tipo de imóvel"),
            widget=forms.Select(
                attrs={
                    "class": "form-select",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
        self.fields["properties_filter_city"] = forms.CharField(
            label=_("Filtrar por Cidade (opcional)"),
            max_length=100,
            initial=config.get("filter_city", ""),
            required=False,
            help_text=_("Deixe em branco para mostrar todas as cidades"),
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                    "placeholder": _("Deixe em branco para mostrar todas as cidades"),
                }
            ),
        )
        self.fields["properties_show_featured_only"] = forms.BooleanField(
            label=_("Mostrar apenas imóveis em destaque"),
            initial=config.get("show_featured_only", False),
            required=False,
        )
        self.fields["properties_limit"] = forms.IntegerField(
            label=_("Limite de imóveis a exibir"),
            initial=config.get("limit", 0),
            required=False,
            min_value=0,
            max_value=100,
            help_text=_("Deixe em 0 para mostrar todos. Máximo: 100"),
            widget=forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem;",
                }
            ),
        )
