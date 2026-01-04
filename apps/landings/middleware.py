"""
Middleware para detecção de tenant (multi-tenant) com validação de segurança.

Este middleware detecta qual landing page deve ser servida baseado no
domínio ou subdomínio da requisição, adicionando o tenant ao objeto request.

SEGURANÇA: Domínios não registrados no sistema retornam 404, mesmo com ALLOWED_HOSTS='*'
"""

import logging

from django.conf import settings
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from .models import LandingPage

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware que detecta qual landing page deve ser servida
    baseado no domínio/subdomínio da requisição.

    Adiciona ao request:
    - request.tenant: A LandingPage correspondente ou None
    - request.is_landing_page: Boolean indicando se é uma requisição de landing page
    
    SEGURANÇA:
    - Domínios não registrados no sistema retornam 404
    - Previne acesso não autorizado mesmo com ALLOWED_HOSTS='*'
    - Loga tentativas de acesso a domínios não registrados
    """

    def process_request(self, request):
        """Processa a requisição para detectar o tenant e validar segurança"""
        # Pega o host da requisição (remove porta se tiver)
        host = request.get_host().split(":")[0].lower()

        # Inicializa o tenant como None
        request.tenant = None
        request.is_landing_page = False

        # Pega o domínio base configurado
        base_domain = getattr(settings, "BASE_DOMAIN", "propzy.com.br")

        # Lista de hosts que NÃO são landing pages (são do sistema principal)
        system_hosts = [
            base_domain,
            f"www.{base_domain}",
            f"app.{base_domain}",
            "localhost",
            "127.0.0.1",
        ]

        # Se for um host do sistema, não é landing page - permite acesso
        if host in system_hosts:
            return

        # Tenta encontrar por domínio personalizado primeiro
        try:
            landing_page = LandingPage.objects.select_related("owner", "theme").get(
                custom_domain=host, is_active=True, is_published=True
            )
            request.tenant = landing_page
            request.is_landing_page = True
            return
        except LandingPage.DoesNotExist:
            pass

        # Tenta encontrar por subdomínio
        if host.endswith(f".{base_domain}"):
            subdomain = host.replace(f".{base_domain}", "")

            # Ignora subdomínios do sistema - permite acesso
            if subdomain in ["www", "app", "api", "admin"]:
                return

            try:
                landing_page = LandingPage.objects.select_related("owner", "theme").get(
                    subdomain=subdomain, is_active=True, is_published=True
                )
                request.tenant = landing_page
                request.is_landing_page = True
                return
            except LandingPage.DoesNotExist:
                pass

        # SEGURANÇA: Se chegou aqui, é um domínio não registrado
        # Loga a tentativa e retorna 404
        logger.warning(
            f"Acesso negado a domínio não registrado: {host} "
            f"(IP: {request.META.get('REMOTE_ADDR')})"
        )
        raise Http404(f"Domínio '{host}' não registrado no sistema.")



