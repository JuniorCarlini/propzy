"""
Dynamic ALLOWED_HOSTS para suportar domínios personalizados multi-tenant.

Este módulo permite que o Django aceite automaticamente:
1. Domínios base configurados em ALLOWED_HOSTS (ex: .propzy.com.br)
2. Domínios personalizados cadastrados no banco de dados (LandingPage.custom_domain)

Isso evita ter que usar ALLOWED_HOSTS=['*'] que seria inseguro.
"""


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
        
        Args:
            host: O hostname a ser verificado (ex: 'orzam.com.br')
            
        Returns:
            bool: True se o host é permitido, False caso contrário
        """
        # Verifica primeiro nos hosts base (mais rápido)
        if super().__contains__(host):
            return True

        # Remove porta se houver (ex: 'orzam.com.br:8000' -> 'orzam.com.br')
        if ':' in host:
            host = host.split(':')[0]

        # Consulta o banco de dados para domínios personalizados
        try:
            from apps.landings.models import LandingPage
            
            # Verifica se existe uma landing page com este domínio personalizado
            # que está ativa e publicada
            return LandingPage.objects.filter(
                custom_domain=host,
                is_active=True,
                is_published=True
            ).exists()
        except Exception:
            # Se houver qualquer erro (banco não inicializado, migration pendente, etc)
            # retorna False para não quebrar a aplicação
            return False

    def __repr__(self):
        """Representação string para debug."""
        return f"DynamicAllowedHosts({self.base_hosts} + custom_domains)"

