"""
Tarefas assíncronas do Celery para Landing Pages
"""
import logging
from celery import shared_task
from django.core.mail import mail_admins

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_ssl_certificate(self, landing_page_id: int, domain: str, email: str):
    """
    Gera certificado SSL para um domínio personalizado

    Args:
        landing_page_id: ID da landing page
        domain: Domínio para gerar certificado
        email: Email para notificações
    """
    from apps.landings.models import LandingPage
    from apps.landings.ssl_manager import ssl_manager

    try:
        logger.info(f"Gerando certificado SSL para {domain}...")

        # Buscar landing page
        landing_page = LandingPage.objects.get(id=landing_page_id)

        # Atualizar status
        landing_page.ssl_status = 'generating'
        landing_page.save(update_fields=['ssl_status'])

        # Gerar certificado
        success, message = ssl_manager.generate_certificate(domain, email)

        if success:
            # Sucesso!
            logger.info(f"✅ Certificado gerado para {domain}")
            landing_page.ssl_status = 'active'
            landing_page.ssl_error = None
            landing_page.save(update_fields=['ssl_status', 'ssl_error'])

            # Notificar administradores
            mail_admins(
                f"SSL Gerado: {domain}",
                f"Certificado SSL gerado com sucesso para {domain}\n\n"
                f"Landing Page: {landing_page.business_name}\n"
                f"Proprietário: {landing_page.owner.email}"
            )

            return {"success": True, "message": message}
        else:
            # Erro
            logger.error(f"❌ Erro ao gerar certificado para {domain}: {message}")
            landing_page.ssl_status = 'error'
            landing_page.ssl_error = message[:500]  # Limitar tamanho
            landing_page.save(update_fields=['ssl_status', 'ssl_error'])

            # Tentar novamente (max 3 vezes)
            raise self.retry(exc=Exception(message), countdown=300)  # Retry em 5 minutos

    except LandingPage.DoesNotExist:
        logger.error(f"Landing page {landing_page_id} não encontrada")
        return {"success": False, "message": "Landing page não encontrada"}

    except Exception as e:
        logger.error(f"Erro inesperado ao gerar certificado: {str(e)}")

        # Atualizar status de erro
        try:
            landing_page = LandingPage.objects.get(id=landing_page_id)
            landing_page.ssl_status = 'error'
            landing_page.ssl_error = str(e)[:500]
            landing_page.save(update_fields=['ssl_status', 'ssl_error'])
        except:
            pass

        raise


@shared_task
def renew_ssl_certificates():
    """
    Renova todos os certificados SSL que estão próximos do vencimento
    Deve ser executado diariamente via Celery Beat
    """
    from apps.landings.ssl_manager import ssl_manager

    logger.info("Iniciando renovação automática de certificados SSL...")

    try:
        renewed, errors = ssl_manager.renew_all_certificates()

        logger.info(f"✅ Renovação concluída: {renewed} renovados, {errors} erros")

        # Notificar administradores se houver renovações
        if renewed > 0:
            mail_admins(
                "Certificados SSL Renovados",
                f"{renewed} certificado(s) SSL foram renovados automaticamente."
            )

        return {"renewed": renewed, "errors": errors}

    except Exception as e:
        logger.error(f"❌ Erro ao renovar certificados: {str(e)}")

        # Notificar administradores sobre erro
        mail_admins(
            "Erro na Renovação de Certificados SSL",
            f"Erro ao renovar certificados SSL:\n\n{str(e)}"
        )

        raise


@shared_task
def check_custom_domain_dns(landing_page_id: int, domain: str):
    """
    Verifica se o DNS do domínio personalizado está configurado corretamente

    Args:
        landing_page_id: ID da landing page
        domain: Domínio para verificar
    """
    import socket
    from apps.landings.models import LandingPage
    from django.conf import settings

    try:
        logger.info(f"Verificando DNS para {domain}...")

        landing_page = LandingPage.objects.get(id=landing_page_id)

        # Resolver DNS
        try:
            ip_address = socket.gethostbyname(domain)
            logger.info(f"DNS de {domain} aponta para {ip_address}")

            # Verificar se aponta para o servidor correto
            # (Aqui você pode adicionar lógica para verificar se é o IP esperado)

            landing_page.dns_status = 'ok'
            landing_page.dns_error = None
            landing_page.save(update_fields=['dns_status', 'dns_error'])

            return {"success": True, "ip": ip_address}

        except socket.gaierror:
            error_msg = f"DNS não configurado ou não propagado ainda"
            logger.warning(f"⚠️ {error_msg} para {domain}")

            landing_page.dns_status = 'error'
            landing_page.dns_error = error_msg
            landing_page.save(update_fields=['dns_status', 'dns_error'])

            return {"success": False, "message": error_msg}

    except LandingPage.DoesNotExist:
        logger.error(f"Landing page {landing_page_id} não encontrada")
        return {"success": False, "message": "Landing page não encontrada"}

    except Exception as e:
        logger.error(f"Erro ao verificar DNS: {str(e)}")
        raise

