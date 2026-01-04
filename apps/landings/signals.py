"""
Signals para Landing Pages
Gera certificados SSL automaticamente quando domínio personalizado é adicionado
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import LandingPage

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=LandingPage)
def detect_custom_domain_change(sender, instance, **kwargs):
    """
    Detecta quando um domínio personalizado é adicionado ou alterado
    """
    if instance.pk:  # Se já existe (não é novo)
        try:
            old_instance = LandingPage.objects.get(pk=instance.pk)

            # Verificar se custom_domain mudou
            if old_instance.custom_domain != instance.custom_domain:
                # Domínio mudou
                if instance.custom_domain:
                    logger.info(f"Domínio personalizado adicionado/alterado: {instance.custom_domain}")
                    # Flag para gerar certificado no post_save
                    instance._custom_domain_changed = True
                else:
                    logger.info(f"Domínio personalizado removido")
                    instance._custom_domain_changed = False
        except LandingPage.DoesNotExist:
            pass


@receiver(post_save, sender=LandingPage)
def generate_ssl_for_custom_domain(sender, instance, created, **kwargs):
    """
    Gera certificado SSL automaticamente quando domínio personalizado é adicionado
    """
    # Verificar se é novo com custom_domain ou se custom_domain mudou
    should_generate = (
        (created and instance.custom_domain) or
        getattr(instance, '_custom_domain_changed', False)
    )

    if should_generate and instance.custom_domain:
        logger.info(f"🔐 Agendando geração de certificado SSL para {instance.custom_domain}")

        # Importar aqui para evitar circular import
        from .tasks import generate_ssl_certificate, check_custom_domain_dns

        try:
            # Primeiro verificar DNS (com delay de 30 segundos)
            check_custom_domain_dns.apply_async(
                args=[instance.id, instance.custom_domain],
                countdown=30
            )

            # Depois gerar certificado (com delay de 2 minutos para dar tempo do DNS propagar)
            generate_ssl_certificate.apply_async(
                args=[
                    instance.id,
                    instance.custom_domain,
                    instance.owner.email or settings.DEFAULT_FROM_EMAIL
                ],
                countdown=120  # 2 minutos de delay
            )

            logger.info(f"✅ Tarefas agendadas para gerar SSL de {instance.custom_domain}")

        except Exception as e:
            logger.error(f"❌ Erro ao agendar geração de SSL: {str(e)}")

