"""
Dynamic ALLOWED_HOSTS para suportar domínios personalizados multi-tenant.

Este módulo permite que o Django aceite automaticamente:
1. Domínios base configurados em ALLOWED_HOSTS (ex: .propzy.com.br)
2. Domínios personalizados cadastrados no banco de dados (LandingPage.custom_domain)

Isso evita ter que usar ALLOWED_HOSTS=['*'] que seria inseguro.
"""
import logging

logger = logging.getLogger(__name__)


class DynamicAllowedHosts(list):
    """
    ALLOWED_HOSTS dinâmico que consulta o banco de dados.

    Permite que domínios personalizados de landing pages sejam automaticamente aceitos
    sem precisar adicionar manualmente ao ALLOWED_HOSTS.
    """

    def __init__(self, base_hosts):
        """
        Inicializa com os hosts base (domínio principal e subdomínios).

        Args:
            base_hosts: Lista de hosts base (ex: ['localhost', '.propzy.com.br'])
        """
        super().__init__(base_hosts)
        self.base_hosts = base_hosts

    def __contains__(self, host):
        """
        Verifica se um host é permitido.

        Primeiro verifica nos hosts base, depois consulta o banco de dados
        para ver se é um domínio personalizado cadastrado.

        USA CACHE para evitar queries repetidas no banco!

        Args:
            host: O hostname a ser verificado (ex: 'orzam.com.br')

        Returns:
            bool: True se o host é permitido, False caso contrário
        """
        logger.debug(f"DynamicAllowedHosts.__contains__() chamado para: {host}")
        
        # Verifica primeiro nos hosts base (mais rápido)
        if super().__contains__(host):
            logger.debug(f"  ✅ '{host}' encontrado nos base_hosts")
            return True

        # Remove porta se houver (ex: 'orzam.com.br:8000' -> 'orzam.com.br')
        if ':' in host:
            host = host.split(':')[0]
            logger.debug(f"  Porta removida, novo host: {host}")

        # Verifica no cache primeiro (TTL de 5 minutos)
        try:
            logger.debug(f"  Importando cache...")
            from django.core.cache import cache
            logger.debug(f"  Cache importado com sucesso!")

            cache_key = f'allowed_host:{host}'
            cached_result = cache.get(cache_key)
            logger.debug(f"  Cache lookup: {cache_key} = {cached_result}")

            if cached_result is not None:
                logger.debug(f"  ✅ Retornando do cache: {cached_result}")
                return cached_result  # True ou False do cache

            # Se não está no cache, consulta o banco
            logger.debug(f"  Importando LandingPage model...")
            from apps.landings.models import LandingPage
            logger.debug(f"  LandingPage importado com sucesso!")

            # Verifica se existe uma landing page com este domínio personalizado
            # que está ativa e publicada
            logger.debug(f"  Fazendo query no banco para custom_domain='{host}'...")
            is_allowed = LandingPage.objects.filter(
                custom_domain=host,
                is_active=True,
                is_published=True
            ).exists()
            logger.debug(f"  Query result: {is_allowed}")

            # Salva no cache por 5 minutos (300 segundos)
            cache.set(cache_key, is_allowed, 300)
            logger.debug(f"  Salvo no cache: {cache_key} = {is_allowed}")

            logger.debug(f"  ✅ Retornando: {is_allowed}")
            return is_allowed

        except Exception as e:
            # Se houver qualquer erro (banco não inicializado, migration pendente, etc)
            # retorna False para não quebrar a aplicação
            logger.error(f"❌ DynamicAllowedHosts error for '{host}': {type(e).__name__}: {e}", exc_info=True)
            return False

    def __repr__(self):
        """Representação string para debug."""
        return f"DynamicAllowedHosts({self.base_hosts} + custom_domains)"

