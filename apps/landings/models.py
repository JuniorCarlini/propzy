"""
Models do app Landings.

Define os modelos para:
- LandingPageTheme: Temas/templates disponíveis
- LandingPage: Landing page de cada usuário
- Property: Imóveis exibidos na landing page
- PropertyImage: Imagens adicionais dos imóveis
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class LandingPageTheme(models.Model):
    """
    Representa um tema instalado no sistema.
    Os temas ficam em templates/landings/themes/<slug>/
    """

    # Identificação
    name = models.CharField(_("Nome"), max_length=100)
    slug = models.SlugField(
        _("Slug"), max_length=50, unique=True, help_text=_("Nome da pasta do tema. Ex: modern, classic")
    )

    # Metadados
    description = models.TextField(_("Descrição"), blank=True)
    author = models.CharField(_("Autor"), max_length=100, blank=True)
    version = models.CharField(_("Versão"), max_length=20, default="1.0.0")

    # Categorização
    CATEGORIES = [
        ("modern", _("Moderno")),
        ("classic", _("Clássico")),
        ("minimal", _("Minimalista")),
        ("luxury", _("Luxuoso")),
        ("corporate", _("Corporativo")),
    ]
    category = models.CharField(_("Categoria"), max_length=20, choices=CATEGORIES, default="modern")

    # Preview
    screenshot = models.ImageField(
        _("Screenshot"), upload_to="themes/screenshots/", blank=True, help_text=_("Preview do tema")
    )

    # Cores padrão (podem ser sobrescritas pelo usuário)
    default_primary_color = models.CharField(_("Cor Primária Padrão"), max_length=7, default="#007bff")
    default_secondary_color = models.CharField(_("Cor Secundária Padrão"), max_length=7, default="#6c757d")

    # Status
    is_active = models.BooleanField(_("Ativo"), default=True, help_text=_("Se desativado, não aparece para seleção"))
    is_premium = models.BooleanField(_("Premium"), default=False, help_text=_("Requer plano premium"))

    # Ordem de exibição
    order = models.PositiveIntegerField(_("Ordem"), default=0)

    # Metadados técnicos
    features = models.JSONField(_("Recursos"), default=list, blank=True, help_text=_("Lista de recursos do tema"))

    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Tema de Landing Page")
        verbose_name_plural = _("Temas de Landing Pages")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def get_template_path(self, template_name: str = "index.html") -> str:
        """Retorna o caminho do template"""
        return f"landings/themes/{self.slug}/{template_name}"

    def get_theme_dir(self) -> Path:
        """Retorna o diretório do tema"""
        base_template_dir = Path(settings.BASE_DIR) / "templates"
        return base_template_dir / "landings" / "themes" / self.slug

    def get_theme_config(self) -> dict:
        """Lê o arquivo theme.json do tema"""
        theme_dir = self.get_theme_dir()
        config_file = theme_dir / "theme.json"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def validate_theme_exists(self):
        """Valida se a pasta do tema existe"""
        theme_dir = self.get_theme_dir()
        if not theme_dir.exists():
            raise ValidationError(f"Pasta do tema não encontrada: {theme_dir}")

        # Valida se tem pelo menos index.html
        index_file = theme_dir / "index.html"
        if not index_file.exists():
            raise ValidationError(f"Arquivo index.html não encontrado no tema: {self.slug}")

    def clean(self):
        """Validação customizada"""
        super().clean()
        # Só valida se o tema já existe (em modo produção)
        # Em desenvolvimento, permite criar o tema antes da pasta
        if not settings.DEBUG:
            self.validate_theme_exists()


class LandingPage(models.Model):
    """Landing page de cada usuário (corretor/imobiliária)"""

    # Relacionamento com o usuário
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="landing_page", verbose_name=_("Proprietário")
    )

    # Domínios
    subdomain = models.SlugField(
        _("Subdomínio"), max_length=50, unique=True, help_text=_("Ex: fulano → fulano.propzy.com.br")
    )
    custom_domain = models.CharField(
        _("Domínio Personalizado"),
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text=_("Ex: www.imobiliariafulano.com.br"),
    )

    # Status SSL do domínio personalizado
    SSL_STATUS_CHOICES = [
        ('none', _('Sem SSL')),
        ('generating', _('Gerando...')),
        ('active', _('Ativo')),
        ('error', _('Erro')),
    ]
    ssl_status = models.CharField(
        _("Status SSL"),
        max_length=20,
        choices=SSL_STATUS_CHOICES,
        default='none',
        help_text=_("Status do certificado SSL do domínio personalizado")
    )
    ssl_error = models.TextField(
        _("Erro SSL"),
        blank=True,
        null=True,
        help_text=_("Mensagem de erro se falhar geração do SSL")
    )

    # Status DNS do domínio personalizado
    DNS_STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('ok', _('Configurado')),
        ('error', _('Erro')),
    ]
    dns_status = models.CharField(
        _("Status DNS"),
        max_length=20,
        choices=DNS_STATUS_CHOICES,
        default='pending',
        help_text=_("Status da configuração DNS do domínio personalizado")
    )
    dns_error = models.TextField(
        _("Erro DNS"),
        blank=True,
        null=True,
        help_text=_("Mensagem de erro se DNS não estiver configurado")
    )

    # Tema selecionado
    theme = models.ForeignKey(
        LandingPageTheme,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Tema"),
        help_text=_("Selecione o tema/layout da landing page"),
    )

    # Dados do negócio
    business_name = models.CharField(_("Nome do Negócio"), max_length=200)
    business_description = models.TextField(_("Descrição"), blank=True)
    logo = models.ImageField(_("Logo"), upload_to="logos/", blank=True)
    hero_image = models.ImageField(_("Imagem Principal/Banner"), upload_to="heroes/", blank=True)

    # Contato
    email = models.EmailField(_("E-mail de Contato"))
    phone = models.CharField(_("Telefone"), max_length=20, blank=True)
    whatsapp = models.CharField(
        _("WhatsApp"), max_length=20, blank=True, help_text=_("Formato: 5569999999999 (DDI+DDD+número)")
    )

    # Endereço
    address = models.CharField(_("Endereço"), max_length=255, blank=True)
    city = models.CharField(_("Cidade"), max_length=100, blank=True)
    state = models.CharField(_("Estado"), max_length=2, blank=True)

    # Redes Sociais
    facebook_url = models.URLField(_("Facebook"), blank=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn"), blank=True)

    # Customização visual
    primary_color = models.CharField(
        _("Cor Primária"), max_length=7, default="#007bff", help_text=_("Formato: #RRGGBB")
    )
    secondary_color = models.CharField(
        _("Cor Secundária"), max_length=7, default="#6c757d", help_text=_("Formato: #RRGGBB")
    )

    # SEO
    meta_title = models.CharField(_("Meta Título"), max_length=60, blank=True, help_text=_("Para SEO (Google)"))
    meta_description = models.CharField(
        _("Meta Descrição"), max_length=160, blank=True, help_text=_("Para SEO (Google)")
    )

    # Status
    is_active = models.BooleanField(_("Ativa"), default=True)
    is_published = models.BooleanField(_("Publicada"), default=False, help_text=_("Visível publicamente"))

    # Metadados
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Landing Page")
        verbose_name_plural = _("Landing Pages")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} ({self.subdomain})"

    def get_full_subdomain(self) -> str:
        """Retorna o subdomínio completo"""
        base_domain = getattr(settings, "BASE_DOMAIN", "propzy.com.br")
        return f"{self.subdomain}.{base_domain}"

    def get_primary_url(self) -> str:
        """Retorna a URL primária (custom domain ou subdomain)"""
        if self.custom_domain:
            return f"https://{self.custom_domain}"
        return f"https://{self.get_full_subdomain()}"


class Property(models.Model):
    """Imóveis disponíveis na landing page"""

    PROPERTY_TYPES = [
        ("house", _("Casa")),
        ("apartment", _("Apartamento")),
        ("commercial", _("Comercial")),
        ("land", _("Terreno")),
        ("farm", _("Fazenda")),
    ]

    TRANSACTION_TYPES = [
        ("sale", _("Venda")),
        ("rent", _("Aluguel")),
        ("both", _("Venda/Aluguel")),
    ]

    landing_page = models.ForeignKey(
        LandingPage, on_delete=models.CASCADE, related_name="properties", verbose_name=_("Landing Page")
    )

    # Informações básicas
    title = models.CharField(_("Título"), max_length=200)
    description = models.TextField(_("Descrição"))
    property_type = models.CharField(_("Tipo"), max_length=20, choices=PROPERTY_TYPES)
    transaction_type = models.CharField(_("Transação"), max_length=10, choices=TRANSACTION_TYPES)

    # Valores
    sale_price = models.DecimalField(
        _("Preço de Venda"), max_digits=12, decimal_places=2, null=True, blank=True
    )
    rent_price = models.DecimalField(
        _("Preço de Aluguel"), max_digits=12, decimal_places=2, null=True, blank=True
    )

    # Características
    bedrooms = models.PositiveIntegerField(_("Quartos"), default=0)
    bathrooms = models.PositiveIntegerField(_("Banheiros"), default=0)
    garage_spaces = models.PositiveIntegerField(_("Vagas"), default=0)
    area = models.DecimalField(_("Área (m²)"), max_digits=10, decimal_places=2)

    # Localização
    address = models.CharField(_("Endereço"), max_length=255)
    neighborhood = models.CharField(_("Bairro"), max_length=100)
    city = models.CharField(_("Cidade"), max_length=100)
    state = models.CharField(_("Estado"), max_length=2)
    zipcode = models.CharField(_("CEP"), max_length=10, blank=True)

    # Imagens (primeira é a principal)
    main_image = models.ImageField(_("Imagem Principal"), upload_to="properties/")

    # Status
    is_featured = models.BooleanField(_("Destaque"), default=False)
    is_active = models.BooleanField(_("Ativo"), default=True)

    # Ordem de exibição
    order = models.PositiveIntegerField(_("Ordem"), default=0)

    # Metadados
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Imóvel")
        verbose_name_plural = _("Imóveis")
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def get_price_display(self) -> str:
        """Retorna o preço formatado"""
        if self.transaction_type == "sale" and self.sale_price:
            return f"R$ {self.sale_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif self.transaction_type == "rent" and self.rent_price:
            return f"R$ {self.rent_price:,.2f}/mês".replace(",", "X").replace(".", ",").replace("X", ".")
        elif self.transaction_type == "both":
            prices = []
            if self.sale_price:
                prices.append(f"Venda: R$ {self.sale_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            if self.rent_price:
                prices.append(
                    f"Aluguel: R$ {self.rent_price:,.2f}/mês".replace(",", "X").replace(".", ",").replace("X", ".")
                )
            return " | ".join(prices)
        return _("Consulte-nos")


class PropertyImage(models.Model):
    """Imagens adicionais do imóvel"""

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images", verbose_name=_("Imóvel"))
    image = models.ImageField(_("Imagem"), upload_to="properties/")
    caption = models.CharField(_("Legenda"), max_length=200, blank=True)
    order = models.PositiveIntegerField(_("Ordem"), default=0)
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)

    class Meta:
        verbose_name = _("Imagem do Imóvel")
        verbose_name_plural = _("Imagens dos Imóveis")
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Imagem {self.order} - {self.property.title}"



