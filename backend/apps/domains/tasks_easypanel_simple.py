"""
Tasks assíncronas para o app domains - VERSÃO EASYPANEL SIMPLIFICADA
Esta versão NÃO usa API - o Traefik faz tudo automaticamente!
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

# Importar dnspython somente se disponível
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logger.warning("dnspython não instalado - verificação DNS limitada")


@shared_task
def verify_domain(domain_id):
    """
    Verifica se um domínio está configurado corretamente
    
    VERSÃO SIMPLIFICADA:
    - Apenas verifica DNS
    - Marca como verificado
    - Traefik gera SSL automaticamente quando receber primeira requisição
    - SEM chamadas de API, SEM complexidade adicional!
    """
    from apps.domains.models import Domain
    
    try:
        domain = Domain.objects.get(id=domain_id)
        
        if not DNS_AVAILABLE:
            logger.warning(f"DNS verification skipped for {domain.domain} - dnspython not available")
            return {
                'status': 'error',
                'message': 'DNS verification not available'
            }
        
        # Tentar resolver DNS
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        
        vps_ip = getattr(settings, 'VPS_IP', None)
        proxy_domain = getattr(settings, 'PROXY_DOMAIN', None)
        
        # Verificar registro A
        try:
            a_records = resolver.resolve(domain.domain, 'A')
            for rdata in a_records:
                ip = str(rdata)
                if vps_ip and ip == vps_ip:
                    domain.is_verified = True
                    domain.verified_at = timezone.now()
                    domain.save()
                    
                    logger.info(f"✅ Domínio {domain.domain} verificado via A record: {ip}")
                    logger.info(f"   Traefik irá gerar SSL automaticamente na primeira requisição")
                    
                    return {
                        'status': 'success',
                        'message': f'Domain verified via A record: {ip}. SSL will be generated automatically by Traefik.'
                    }
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            pass
        
        # Verificar registro CNAME
        try:
            cname_records = resolver.resolve(domain.domain, 'CNAME')
            for rdata in cname_records:
                target = str(rdata.target).rstrip('.')
                if proxy_domain and target == proxy_domain:
                    domain.is_verified = True
                    domain.verified_at = timezone.now()
                    domain.save()
                    
                    logger.info(f"✅ Domínio {domain.domain} verificado via CNAME: {target}")
                    logger.info(f"   Traefik irá gerar SSL automaticamente na primeira requisição")
                    
                    return {
                        'status': 'success',
                        'message': f'Domain verified via CNAME: {target}. SSL will be generated automatically by Traefik.'
                    }
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            pass
        
        return {
            'status': 'error',
            'message': 'No DNS records found'
        }
        
    except Domain.DoesNotExist:
        return {
            'status': 'error',
            'message': 'Domain not found'
        }
    except Exception as e:
        logger.error(f"Error verifying domain {domain_id}: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def verify_all_pending_domains():
    """
    Verifica todos os domínios pendentes de verificação
    
    Roda periodicamente via Celery Beat (ex: a cada 30 minutos)
    """
    from apps.domains.models import Domain
    
    pending_domains = Domain.objects.filter(is_verified=False)
    results = []
    
    for domain in pending_domains:
        result = verify_domain(str(domain.id))
        results.append({
            'domain': domain.domain,
            'result': result
        })
    
    return {
        'total': pending_domains.count(),
        'results': results
    }


# =============================================================================
# NOTA: Não precisa de task para gerar SSL!
# =============================================================================
# O Traefik faz isso automaticamente:
# 1. Cliente acessa domínio pela primeira vez
# 2. Traefik detecta que não tem certificado
# 3. Traefik chama Let's Encrypt
# 4. Certificado é gerado em segundos
# 5. Requisição é servida com SSL
#
# Tudo automático, sem código adicional! 🎉
# =============================================================================


@shared_task
def check_ssl_status():
    """
    Task opcional para monitorar status dos domínios
    Apenas para auditoria/logs - não afeta funcionalidade
    """
    from apps.domains.models import Domain
    
    verified_domains = Domain.objects.filter(is_verified=True)
    results = []
    
    for domain in verified_domains:
        results.append({
            'domain': domain.domain,
            'verified': domain.is_verified,
            'verified_at': domain.verified_at.isoformat() if domain.verified_at else None,
            'note': 'SSL managed automatically by Traefik'
        })
    
    return {
        'total': verified_domains.count(),
        'domains': results
    }

