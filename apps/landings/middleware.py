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
    - Valida formato do hostname (anti-injection)
    - Protegido contra SQL injection (Django ORM)
    - Protegido contra Host Header Injection
    - Loga tentativas de acesso a domínios não registrados
    """
    
    @staticmethod
    def _is_valid_hostname(hostname: str) -> bool:
        """
        Valida se o hostname é seguro e está em formato correto.
        
        SEGURANÇA:
        - Previne CRLF injection
        - Previne Unicode tricks
        - Previne SQL injection via hostname
        - Valida formato RFC 1123
        """
        import re
        
        # Tamanho máximo de hostname (RFC 1123)
        if len(hostname) > 253:
            return False
        
        # Previne CRLF injection
        if '\r' in hostname or '\n' in hostname or '\x00' in hostname:
            return False
        
        # Previne Unicode tricks (apenas ASCII)
        try:
            hostname.encode('ascii')
        except UnicodeEncodeError:
            return False
        
        # Valida formato: letras, números, hífens e pontos apenas
        # RFC 1123: hostname = (dominio\.)+tld
        pattern = r'^([a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?\.)*[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$'
        if not re.match(pattern, hostname):
            return False
        
        # Previne hostname que é apenas números (pode ser IP)
        if hostname.replace('.', '').isdigit():
            # Permite apenas se for localhost/127.0.0.1
            if hostname in ('127.0.0.1', 'localhost'):
                return True
            return False
        
        return True
    
    @staticmethod
    def _is_valid_subdomain(subdomain: str) -> bool:
        """
        Valida se o subdomínio é seguro.
        
        SEGURANÇA:
        - Apenas letras, números e hífens
        - Máximo 63 caracteres (RFC 1123)
        - Não pode começar ou terminar com hífen
        """
        import re
        
        if not subdomain or len(subdomain) > 63:
            return False
        
        # Apenas ASCII
        try:
            subdomain.encode('ascii')
        except UnicodeEncodeError:
            return False
        
        # Padrão: letras, números, hífens (não no início/fim)
        pattern = r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$'
        return bool(re.match(pattern, subdomain))

    def process_request(self, request):
        """Processa a requisição para detectar o tenant e validar segurança"""
        # SEGURANÇA: Pega o host da requisição com validação rigorosa
        try:
            # request.get_host() já valida contra ALLOWED_HOSTS do Django
            # e checa X-Forwarded-Host se USE_X_FORWARDED_HOST=True
            host = request.get_host().split(":")[0].lower()
            
            # PROTEÇÃO: Valida formato do host (previne CRLF, Unicode tricks, etc)
            if not self._is_valid_hostname(host):
                logger.warning(
                    f"Host inválido detectado: {repr(host)} "
                    f"(IP: {request.META.get('REMOTE_ADDR')})"
                )
                raise Http404("Host inválido")
                
        except Exception as e:
            logger.error(f"Erro ao processar host: {e}")
            raise Http404("Host inválido")

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
        # SEGURANÇA: Django ORM usa prepared statements, protegido contra SQL injection
        try:
            landing_page = LandingPage.objects.select_related("owner", "theme").get(
                custom_domain=host,  # Django ORM sanitiza automaticamente
                is_active=True,
                is_published=True
            )
            request.tenant = landing_page
            request.is_landing_page = True
            logger.info(f"Tenant encontrado: {host} -> LandingPage ID {landing_page.id}")
            return
        except LandingPage.DoesNotExist:
            pass
        except LandingPage.MultipleObjectsReturned:
            # SEGURANÇA: Se houver duplicatas, loga e retorna 404
            logger.error(f"Múltiplas landing pages encontradas para: {host}")
            raise Http404("Configuração inválida")

        # Tenta encontrar por subdomínio
        if host.endswith(f".{base_domain}"):
            subdomain = host.replace(f".{base_domain}", "")

            # Ignora subdomínios do sistema - permite acesso
            if subdomain in ["www", "app", "api", "admin"]:
                return

            try:
                # SEGURANÇA: Valida subdomain antes de query
                if not self._is_valid_subdomain(subdomain):
                    logger.warning(f"Subdomínio inválido: {repr(subdomain)}")
                    raise Http404("Subdomínio inválido")
                
                landing_page = LandingPage.objects.select_related("owner", "theme").get(
                    subdomain=subdomain,  # Django ORM sanitiza automaticamente
                    is_active=True,
                    is_published=True
                )
                request.tenant = landing_page
                request.is_landing_page = True
                logger.info(f"Tenant encontrado: {subdomain}.{base_domain} -> LandingPage ID {landing_page.id}")
                return
            except LandingPage.DoesNotExist:
                pass
            except LandingPage.MultipleObjectsReturned:
                logger.error(f"Múltiplas landing pages encontradas para subdomínio: {subdomain}")
                raise Http404("Configuração inválida")

        # SEGURANÇA: Se chegou aqui, é um domínio não registrado
        # Loga a tentativa e retorna 404
        logger.warning(
            f"Acesso negado a domínio não registrado: {host} "
            f"(IP: {request.META.get('REMOTE_ADDR')})"
        )
        raise Http404(f"Domínio '{host}' não registrado no sistema.")



