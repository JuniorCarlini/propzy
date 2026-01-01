"""
Tasks assíncronas para o app domains
"""
import subprocess
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
                    
                    # Gerar certificado SSL automaticamente
                    generate_ssl_certificate.delay(domain_id)
                    
                    return {
                        'status': 'success',
                        'message': f'Domain verified via A record: {ip}'
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
                    
                    # Gerar certificado SSL automaticamente
                    generate_ssl_certificate.delay(domain_id)
                    
                    return {
                        'status': 'success',
                        'message': f'Domain verified via CNAME: {target}'
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


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_ssl_certificate(self, domain_id):
    """
    Gera certificado SSL Let's Encrypt para um domínio
    Roda em background sem causar downtime
    """
    from apps.domains.models import Domain
    
    try:
        domain = Domain.objects.get(id=domain_id)
        domain_name = domain.domain
        
        logger.info(f"Iniciando geração de certificado SSL para {domain_name}")
        
        # Verificar se domínio está verificado
        if not domain.is_verified:
            logger.warning(f"Domínio {domain_name} não verificado - pulando geração de certificado")
            return {
                'status': 'skipped',
                'message': 'Domain not verified'
            }
        
        # Verificar se é subdomínio do propzy.com.br (já coberto pelo wildcard)
        if domain_name.endswith('.propzy.com.br'):
            logger.info(f"Domínio {domain_name} coberto por wildcard - certificado já existe")
            return {
                'status': 'success',
                'message': 'Covered by wildcard certificate'
            }
        
        # Email para certificado
        email = getattr(settings, 'CERTBOT_EMAIL', 'admin@propzy.com.br')
        
        # Comando para gerar certificado via HTTP challenge (sem parar Nginx)
        # Usa webroot que já está configurado em /.well-known/acme-challenge/
        cmd = [
            'certbot', 'certonly',
            '--webroot',
            '--webroot-path', '/root/apps/propzy/infra/nginx/certbot',
            '-d', domain_name,
            '-d', f'www.{domain_name}',
            '--email', email,
            '--agree-tos',
            '--non-interactive',
            '--quiet'
        ]
        
        logger.info(f"Executando: {' '.join(cmd)}")
        
        # Executar comando
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Certificado gerado com sucesso para {domain_name}")
            
            # Recarregar Nginx (sem downtime!)
            reload_cmd = [
                'docker', 'compose', '-f', '/root/apps/propzy/infra/docker-compose.yml',
                'exec', '-T', 'nginx', 'nginx', '-s', 'reload'
            ]
            
            subprocess.run(reload_cmd, capture_output=True, timeout=30)
            logger.info(f"✅ Nginx recarregado para {domain_name}")
            
            return {
                'status': 'success',
                'message': f'SSL certificate generated for {domain_name}'
            }
        else:
            error_msg = result.stderr or result.stdout
            logger.error(f"❌ Erro ao gerar certificado para {domain_name}: {error_msg}")
            
            # Retry se falhar
            raise self.retry(exc=Exception(error_msg))
            
    except Domain.DoesNotExist:
        logger.error(f"Domínio {domain_id} não encontrado")
        return {
            'status': 'error',
            'message': 'Domain not found'
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout ao gerar certificado para {domain_id}")
        raise self.retry(exc=Exception('Certificate generation timeout'))
    except Exception as e:
        logger.error(f"Erro ao gerar certificado para {domain_id}: {str(e)}")
        raise self.retry(exc=e)


@shared_task
def renew_certificates():
    """
    Renova todos os certificados Let's Encrypt
    Executado via cron 2x por dia
    """
    try:
        logger.info("Iniciando renovação de certificados")
        
        # Comando para renovar certificados
        cmd = ['certbot', 'renew', '--quiet']
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Certificados renovados com sucesso")
            
            # Copiar certificados atualizados
            copy_cmd = ['/root/apps/propzy/infra/scripts/copy-certificates.sh']
            subprocess.run(copy_cmd, capture_output=True, timeout=30)
            
            # Recarregar Nginx
            reload_cmd = [
                'docker', 'compose', '-f', '/root/apps/propzy/infra/docker-compose.yml',
                'exec', '-T', 'nginx', 'nginx', '-s', 'reload'
            ]
            subprocess.run(reload_cmd, capture_output=True, timeout=30)
            
            logger.info("✅ Nginx recarregado após renovação")
            
            return {
                'status': 'success',
                'message': 'Certificates renewed successfully'
            }
        else:
            error_msg = result.stderr or result.stdout
            logger.warning(f"Renovação retornou com código {result.returncode}: {error_msg}")
            
            return {
                'status': 'warning',
                'message': error_msg or 'No certificates needed renewal'
            }
            
    except Exception as e:
        logger.error(f"Erro ao renovar certificados: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }
