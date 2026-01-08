"""
Context processors do app Core - Adiciona dados globais aos templates
"""

from typing import Any


def onboarding_progress(request: Any) -> dict[str, Any]:
    """
    Adiciona informações de progresso do onboarding ao contexto dos templates.

    Args:
        request: Objeto HttpRequest do Django

    Returns:
        Dict com informações de onboarding (vazio se usuário não estiver autenticado)
    """
    if not request.user.is_authenticated:
        return {"onboarding_progress": None}

    try:
        from apps.core.utils import OnboardingProgressCalculator
        from apps.core.models import OnboardingStatus

        progress = OnboardingProgressCalculator.calculate(request.user)

        # Adicionar site ao contexto se disponível
        site = None
        try:
            site = request.user.site
        except Exception:
            pass

        # Verificar status de onboarding no banco de dados
        onboarding_status = None
        try:
            onboarding_status = OnboardingStatus.get_or_create_for_user(request.user)
        except Exception:
            pass

        return {
            "onboarding_progress": progress,
            "site": site,
            "onboarding_status": onboarding_status,
        }
    except Exception:
        return {"onboarding_progress": None, "site": None, "onboarding_status": None}

