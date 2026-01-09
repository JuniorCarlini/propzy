"""
Models do app Properties - Imóveis e suas imagens
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Property(models.Model):
    """Imóveis disponíveis nas landing pages"""

    PROPERTY_TYPES = [
        ("house", _("Casa")),
        ("apartment", _("Apartamento")),
        ("commercial", _("Comercial")),
        ("land", _("Terreno")),
        ("farm", _("Fazenda")),
    ]

    CATEGORIES = [
        ("urban", _("Urbano")),
        ("rural", _("Rural")),
    ]

    TRANSACTION_TYPES = [
        ("sale", _("Venda")),
        ("rent", _("Aluguel")),
        ("both", _("Venda/Aluguel")),
    ]

    site = models.ForeignKey(
        "landings.Site", on_delete=models.CASCADE, related_name="properties", verbose_name=_("Site")
    )

    # Informações básicas
    title = models.CharField(_("Título"), max_length=200)
    description = models.TextField(_("Descrição"), blank=True)
    property_type = models.CharField(_("Tipo"), max_length=20, choices=PROPERTY_TYPES)
    category = models.CharField(_("Categoria"), max_length=10, choices=CATEGORIES, default="urban")
    transaction_type = models.CharField(_("Transação"), max_length=10, choices=TRANSACTION_TYPES)

    # Valores
    sale_price = models.DecimalField(_("Preço de Venda"), max_digits=12, decimal_places=2, null=True, blank=True)
    rent_price = models.DecimalField(_("Preço de Aluguel"), max_digits=12, decimal_places=2, null=True, blank=True)
    original_sale_price = models.DecimalField(
        _("Preço Anterior de Venda"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Preço anterior para exibir em promoções"),
    )
    original_rent_price = models.DecimalField(
        _("Preço Anterior de Aluguel"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Preço anterior para exibir em promoções"),
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
    # main_image é definido automaticamente quando uma imagem adicional é marcada como principal
    main_image = models.ImageField(_("Imagem Principal"), upload_to="properties/", null=True, blank=True)

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

    def format_price(self, price) -> str:
        """Formata um preço para exibição"""
        if not price:
            return ""
        return f"R$ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def has_promotion(self) -> bool:
        """Verifica se o imóvel está em promoção"""
        if self.transaction_type == "sale":
            return bool(self.original_sale_price and self.sale_price and self.original_sale_price > self.sale_price)
        elif self.transaction_type == "rent":
            return bool(self.original_rent_price and self.rent_price and self.original_rent_price > self.rent_price)
        elif self.transaction_type == "both":
            sale_promo = bool(
                self.original_sale_price and self.sale_price and self.original_sale_price > self.sale_price
            )
            rent_promo = bool(
                self.original_rent_price and self.rent_price and self.original_rent_price > self.rent_price
            )
            return sale_promo or rent_promo
        return False


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
