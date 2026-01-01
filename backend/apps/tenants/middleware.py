"""
Middleware para identificação de Tenant baseado no domínio da requisição.
Este é o ponto crítico do sistema multi-tenant.
"""
from django.http import Http404, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .models import Tenant
from apps.domains.models import Domain


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware que identifica o tenant baseado no Host da requisição HTTP.
    
    Fluxo:
    1. Extrai o Host da requisição
    2. Busca o domínio na tabela Domain
    3. Associa o tenant à request
    4. Bloqueia domínios não verificados
    """
    
    def process_request(self, request):
        host = request.get_host().split(':')[0]  # Remove porta se houver
        
        try:
            # Buscar domínio na tabela Domain
            domain_obj = Domain.objects.select_related('tenant').get(domain=host)
            
            # Verificar se o domínio está verificado
            if not domain_obj.is_verified:
                return HttpResponseForbidden(
                    "Domain not verified. Please complete DNS configuration."
                )
            
            # Verificar se o tenant está ativo
            if not domain_obj.tenant.is_active:
                return HttpResponseForbidden(
                    "Tenant account is inactive."
                )
            
            # Associar tenant à request
            request.tenant = domain_obj.tenant
            request.domain = domain_obj
            
        except Domain.DoesNotExist:
            # Domínio não encontrado - permitir acesso para domínios específicos
            request.tenant = None
            request.domain = None
            
            # Permitir acesso apenas a domínios específicos (landing page, app.propzy.com.br)
            allowed_hosts = [
                'propzy.com.br',
                'www.propzy.com.br',
                'app.propzy.com.br',
                'localhost',
                '127.0.0.1',
            ]
            
            # Em desenvolvimento, permitir qualquer host
            from django.conf import settings
            if settings.DEBUG:
                pass  # Permitir em desenvolvimento
            else:
                # Em produção, verificar se é IP do VPS ou domínio permitido
                vps_ip = getattr(settings, 'VPS_IP', None)
                if vps_ip and host == vps_ip:
                    pass  # Permitir acesso via IP do VPS
                elif host not in allowed_hosts:
                    raise Http404("Domain not found")
        
        return None

