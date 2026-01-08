"""
Models do app Landings - Site de cada usuário

Os modelos foram reorganizados:
- User: movido para apps.core
- Theme: movido para apps.themes
- Property/PropertyImage: movidos para apps.properties
"""

import re
import unicodedata

from django.db import models
from django.utils.translation import gettext_lazy as _


class Site(models.Model):
    """Site de cada usuário (corretor/imobiliária)"""

    # Relacionamento com o usuário
    # Usa string para evitar problemas durante reload do Django
    owner = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="site", verbose_name=_("Proprietário")
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
        ("none", _("Sem SSL")),
        ("generating", _("Gerando...")),
        ("active", _("Ativo")),
        ("error", _("Erro")),
    ]
    ssl_status = models.CharField(
        _("Status SSL"),
        max_length=20,
        choices=SSL_STATUS_CHOICES,
        default="none",
        help_text=_("Status do certificado SSL do domínio personalizado"),
    )
    ssl_error = models.TextField(
        _("Erro SSL"), blank=True, null=True, help_text=_("Mensagem de erro se falhar geração do SSL")
    )

    # Status DNS do domínio personalizado
    DNS_STATUS_CHOICES = [
        ("pending", _("Pendente")),
        ("ok", _("Configurado")),
        ("error", _("Erro")),
    ]
    dns_status = models.CharField(
        _("Status DNS"),
        max_length=20,
        choices=DNS_STATUS_CHOICES,
        default="pending",
        help_text=_("Status da configuração DNS do domínio personalizado"),
    )
    dns_error = models.TextField(
        _("Erro DNS"), blank=True, null=True, help_text=_("Mensagem de erro se DNS não estiver configurado")
    )

    # Tema selecionado
    theme = models.ForeignKey(
        "themes.Theme",  # Referência ao app themes
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Tema"),
        help_text=_("Selecione o tema/layout do site"),
    )

    # Dados do negócio
    business_name = models.CharField(_("Nome do Negócio"), max_length=200)
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
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ["-created_at"]
        db_table = "landings_landingpage"  # Mantém nome da tabela para compatibilidade

    def __str__(self):
        return f"{self.business_name} ({self.subdomain})"

    def get_full_subdomain(self) -> str:
        """Retorna o subdomínio completo"""
        from django.conf import settings

        base_domain = getattr(settings, "BASE_DOMAIN", "propzy.com.br")
        return f"{self.subdomain}.{base_domain}"

    def get_primary_url(self) -> str:
        """Retorna a URL primária (custom domain ou subdomain)"""
        if self.custom_domain:
            return f"https://{self.custom_domain}"
        return f"https://{self.get_full_subdomain()}"

    @staticmethod
    def generate_subdomain_from_business_name(business_name: str) -> str:
        """
        Gera um subdomínio válido baseado no nome do negócio.
        Remove acentos, espaços, caracteres especiais e limita o tamanho.
        """
        if not business_name:
            return "site"

        # Normalizar e remover acentos
        nfkd = unicodedata.normalize('NFKD', business_name)
        text = ''.join([c for c in nfkd if not unicodedata.combining(c)])

        # Converter para minúsculas e remover caracteres especiais
        text = text.lower().strip()
        # Substituir espaços e caracteres especiais por hífen
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        # Remover hífens no início e fim
        text = text.strip('-')
        # Limitar tamanho (máximo 50 caracteres para SlugField)
        text = text[:50]

        # Se ficar vazio, usar fallback
        if not text:
            text = "site"

        return text

    def update_subdomain_from_business_name(self):
        """
        Atualiza o subdomínio baseado no nome do negócio.
        Verifica se já existe e adiciona sufixo numérico se necessário.
        """
        if not self.business_name:
            return

        base_subdomain = self.generate_subdomain_from_business_name(self.business_name)
        new_subdomain = base_subdomain

        # Verificar se já existe (exceto o próprio site)
        counter = 1
        while Site.objects.filter(subdomain=new_subdomain).exclude(pk=self.pk).exists():
            # Adicionar sufixo numérico
            suffix = f"-{counter}"
            max_length = 50 - len(suffix)
            new_subdomain = base_subdomain[:max_length] + suffix
            counter += 1

            # Proteção contra loop infinito
            if counter > 1000:
                # Usar timestamp como fallback
                import time
                new_subdomain = f"site-{int(time.time())}"
                break

        self.subdomain = new_subdomain

    def get_design(self):
        """Retorna o design do site, criando se não existir."""
        design, created = SiteDesign.objects.get_or_create(site=self)
        return design


class ThemeSectionConfig(models.Model):
    """Configurações de seções do tema para cada site"""

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="theme_config",
        verbose_name=_("Site"),
    )

    # Configurações em JSON estruturado
    sections_config = models.JSONField(
        _("Configurações das Seções"),
        default=dict,
        blank=True,
        help_text=_("Configurações de cada seção do tema"),
    )

    # Ordem das seções
    sections_order = models.JSONField(
        _("Ordem das Seções"),
        default=list,
        blank=True,
        help_text=_("Lista com a ordem de exibição das seções"),
    )

    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Configuração do Tema")
        verbose_name_plural = _("Configurações dos Temas")

    def __str__(self):
        return f"Configuração do tema - {self.site.business_name}"

    def get_section_config(self, section_key: str) -> dict:
        """Retorna as configurações de uma seção específica"""
        return self.sections_config.get(section_key, {})

    def is_section_enabled(self, section_key: str) -> bool:
        """Verifica se uma seção está habilitada"""
        section_config = self.get_section_config(section_key)
        return section_config.get("enabled", True)


class SiteDesign(models.Model):
    """
    Modelo para armazenar as configurações de design do site.
    Separa as cores e estilos do modelo Site principal.
    """

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="design",
        verbose_name=_("Site"),
    )

    # Cores principais
    primary_color = models.CharField(
        _("Cor Primária"),
        max_length=7,
        default="#006DFF",
        help_text=_("Cor principal do tema (formato: #RRGGBB)"),
    )
    secondary_color = models.CharField(
        _("Cor Secundária"),
        max_length=7,
        default="#6c757d",
        help_text=_("Cor secundária do tema (formato: #RRGGBB)"),
    )
    tertiary_color = models.CharField(
        _("Cor Terciária"),
        max_length=7,
        default="#9333ea",
        help_text=_("Cor terciária do tema (formato: #RRGGBB)"),
    )
    quaternary_color = models.CharField(
        _("Cor Quaternária"),
        max_length=7,
        default="#f59e0b",
        help_text=_("Cor quaternária do tema (formato: #RRGGBB)"),
    )

    # Cores de status
    success_color = models.CharField(
        _("Cor de Sucesso"),
        max_length=7,
        default="#10b981",
        help_text=_("Cor para mensagens de sucesso (formato: #RRGGBB)"),
    )
    danger_color = models.CharField(
        _("Cor de Erro"),
        max_length=7,
        default="#ef4444",
        help_text=_("Cor para mensagens de erro (formato: #RRGGBB)"),
    )
    warning_color = models.CharField(
        _("Cor de Aviso"),
        max_length=7,
        default="#f59e0b",
        help_text=_("Cor para mensagens de aviso (formato: #RRGGBB)"),
    )
    info_color = models.CharField(
        _("Cor de Informação"),
        max_length=7,
        default="#3b82f6",
        help_text=_("Cor para mensagens informativas (formato: #RRGGBB)"),
    )

    # Cores de texto
    text_primary_color = models.CharField(
        _("Cor de Texto Primária"),
        max_length=7,
        default="#13112F",
        help_text=_("Cor principal do texto (formato: #RRGGBB)"),
    )
    text_secondary_color = models.CharField(
        _("Cor de Texto Secundária"),
        max_length=7,
        default="#585F76",
        help_text=_("Cor secundária do texto (formato: #RRGGBB)"),
    )

    # Cores de fundo e bordas
    background_color = models.CharField(
        _("Cor de Fundo"),
        max_length=7,
        default="#EBECF4",
        help_text=_("Cor de fundo principal (formato: #RRGGBB)"),
    )
    border_color = models.CharField(
        _("Cor de Borda"),
        max_length=7,
        default="#d8dae8",
        help_text=_("Cor das bordas (formato: #RRGGBB)"),
    )

    created_at = models.DateTimeField(_("Data de Criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de Atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Design do Site")
        verbose_name_plural = _("Designs dos Sites")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Design de {self.site.business_name or self.site.owner.email}"
