"""
Utilitários do app Core - Cálculo de progresso de onboarding
"""

from typing import Any

from django.utils.translation import gettext_lazy as _


class OnboardingProgressCalculator:
    """
    Calcula o progresso do onboarding do usuário baseado no estado atual do site.
    """

    STEPS = [
        {
            "key": "add_property",
            "title": _("Cadastrar Imóvel"),
            "description": _("Adicione pelo menos 1 imóvel ao seu site"),
            "icon": "fa-home",
            "url_name": "properties:property_list",
            "check_method": "check_has_property",
        },
        {
            "key": "configure_basic",
            "title": _("Dados Básicos"),
            "description": _("Configure as informações básicas do seu site"),
            "icon": "fa-address-card",
            "url_name": "landings:dashboard_config_basic",
            "check_method": "check_basic_configured",
        },
        {
            "key": "configure_theme",
            "title": _("Temas e Layout"),
            "description": _("Escolha e personalize o tema do seu site"),
            "icon": "fa-palette",
            "url_name": "landings:dashboard_config_theme",
            "check_method": "check_theme_configured",
        },
        {
            "key": "configure_domain",
            "title": _("Configurar Domínio"),
            "description": _("Configure seu domínio personalizado (opcional)"),
            "icon": "fa-globe",
            "url_name": "landings:dashboard_config_domain",
            "check_method": "check_domain_configured",
        },
    ]

    @classmethod
    def calculate(cls, user: Any) -> dict[str, Any]:
        """
        Calcula o progresso do onboarding para um usuário.

        Args:
            user: Instância do modelo User

        Returns:
            Dict com informações do progresso:
            - steps: Lista de etapas com status
            - completed_count: Número de etapas concluídas
            - total_count: Total de etapas
            - percentage: Porcentagem de conclusão
        """
        try:
            site = user.site
        except Exception:
            # Se não tiver site, todas as etapas estão pendentes
            site = None

        steps = []
        completed_count = 0

        for step_config in cls.STEPS:
            check_method = getattr(cls, step_config["check_method"])
            is_completed = check_method(site) if site else False

            if is_completed:
                completed_count += 1

            steps.append(
                {
                    **step_config,
                    "completed": is_completed,
                }
            )

        total_count = len(cls.STEPS)
        percentage = int((completed_count / total_count) * 100) if total_count > 0 else 0

        return {
            "steps": steps,
            "completed_count": completed_count,
            "total_count": total_count,
            "percentage": percentage,
            "all_completed": completed_count == total_count,
        }

    @staticmethod
    def check_has_property(site: Any) -> bool:
        """Verifica se o site tem pelo menos 1 imóvel cadastrado."""
        if not site:
            return False
        try:
            from apps.properties.models import Property

            return Property.objects.filter(site=site).exists()
        except Exception:
            return False

    @staticmethod
    def check_basic_configured(site: Any) -> bool:
        """Verifica se os dados básicos estão configurados."""
        if not site:
            return False
        # Verifica se tem nome do negócio, email e telefone
        return bool(site.business_name and site.email and site.phone)

    @staticmethod
    def check_theme_configured(site: Any) -> bool:
        """Verifica se o tema está configurado."""
        if not site:
            return False
        # Verifica se tem um tema selecionado
        return bool(site.theme)

    @staticmethod
    def check_domain_configured(site: Any) -> bool:
        """Verifica se o domínio está configurado (mesmo que seja apenas o gratuito)."""
        if not site:
            return False
        # Considera configurado se tem subdomínio (sempre tem) ou domínio personalizado
        return bool(site.subdomain)

