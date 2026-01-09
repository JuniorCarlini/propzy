"""
Signals para Sites
Gera certificados SSL automaticamente quando domínio personalizado é adicionado
"""

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Site

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Site)
def detect_custom_domain_change(sender, instance, **kwargs):
    """
    Detecta quando um domínio personalizado é adicionado ou alterado
    """
    if instance.pk:  # Se já existe (não é novo)
        try:
            old_instance = Site.objects.get(pk=instance.pk)

            # Verificar se custom_domain mudou
            if old_instance.custom_domain != instance.custom_domain:
                # Domínio mudou
                if instance.custom_domain:
                    logger.info(f"Domínio personalizado adicionado/alterado: {instance.custom_domain}")
                    # Flag para gerar certificado no post_save
                    instance._custom_domain_changed = True
                else:
                    logger.info("Domínio personalizado removido")
                    instance._custom_domain_changed = False

            # Verificar se business_name mudou para atualizar subdomain automaticamente
            if old_instance.business_name != instance.business_name:
                logger.info(f"Business name mudou de '{old_instance.business_name}' para '{instance.business_name}'")
                # Flag para atualizar subdomain no post_save
                instance._business_name_changed = True
        except Site.DoesNotExist:
            pass


@receiver(post_save, sender=Site)
def generate_ssl_for_custom_domain(sender, instance, created, **kwargs):
    """
    Gera certificado SSL automaticamente quando domínio personalizado é adicionado
    E atualiza subdomain quando business_name muda
    """
    # Atualizar subdomain se business_name mudou
    if getattr(instance, "_business_name_changed", False):
        logger.info("🔄 Atualizando subdomain devido a mudança no business_name")
        try:
            instance.update_subdomain_from_business_name()
            # Salvar apenas o subdomain para evitar loop infinito (post_save chamaria novamente)
            Site.objects.filter(pk=instance.pk).update(subdomain=instance.subdomain)
            logger.info(f"✅ Subdomain atualizado para: {instance.subdomain}")
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar subdomain: {str(e)}")

    # Verificar se é novo com custom_domain ou se custom_domain mudou
    should_generate = (created and instance.custom_domain) or getattr(instance, "_custom_domain_changed", False)

    if should_generate and instance.custom_domain:
        logger.info(f"🔐 Agendando geração de certificado SSL para {instance.custom_domain}")

        # Importar aqui para evitar circular import
        # ATUALIZADO: Tasks movidas para apps.infrastructure
        from apps.infrastructure.tasks import check_custom_domain_dns

        try:
            # Verificar DNS após 5 minutos (dar tempo inicial para propagação)
            # A propagação pode levar até 2 horas, então faremos verificações periódicas
            check_custom_domain_dns.apply_async(args=[instance.id, instance.custom_domain], countdown=300)  # 5 min

            # Verificações adicionais após 30 minutos, 1 hora e 2 horas
            check_custom_domain_dns.apply_async(args=[instance.id, instance.custom_domain], countdown=1800)  # 30 min
            check_custom_domain_dns.apply_async(args=[instance.id, instance.custom_domain], countdown=3600)  # 1 hora
            check_custom_domain_dns.apply_async(args=[instance.id, instance.custom_domain], countdown=7200)  # 2 horas

            # Gerar certificado SSL após primeira verificação bem-sucedida (será verificado na task)
            # A task de DNS verificará e agendará o SSL quando estiver pronto

            logger.info(f"✅ Tarefas agendadas para gerar SSL de {instance.custom_domain}")

        except Exception as e:
            logger.error(f"❌ Erro ao agendar geração de SSL: {str(e)}")
