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
    # Verificar se request.user existe (pode não existir antes do middleware de autenticação)
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {"onboarding_progress": None}

    try:
        from apps.core.models import OnboardingStatus
        from apps.core.utils import OnboardingProgressCalculator

        progress = OnboardingProgressCalculator.calculate(request.user)

        # Adicionar site ao contexto se disponível
        site = None
        try:
            if hasattr(request.user, "site"):
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
        # Em caso de qualquer erro, retornar valores padrão seguros
        return {"onboarding_progress": None, "site": None, "onboarding_status": None}
