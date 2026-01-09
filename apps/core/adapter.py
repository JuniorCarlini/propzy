# pylint: disable=abstract-method
"""
Adapter customizado do django-allauth
"""

from typing import Any
from urllib.parse import urlparse

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    """
    Adapter que desabilita cadastro público.
    Usuários só podem ser criados por administradores.

    Também trata redirecionamentos após login para garantir que
    logins feitos através de subdomínios redirecionem para o domínio principal.
    """

    def is_open_for_signup(self, _request: Any) -> bool:
        """Desabilita o fluxo de auto-registro."""
        return False

    def get_login_redirect_url(self, request: Any) -> str:
        """
        Redireciona para o domínio principal após login se o login foi feito através de um subdomínio.

        Isso garante que usuários não permaneçam no subdomínio após fazer login,
        já que o subdomínio é apenas para exibição pública do site.
        """
        # Verifica se há um parâmetro 'next' na URL (redirecionamento solicitado)
        next_url = request.GET.get("next") or request.POST.get("next")

        # Se houver um 'next', verifica se é uma URL completa
        if next_url:
            try:
                parsed = urlparse(next_url)
                # Se for uma URL completa (com scheme), usa ela
                if parsed.scheme:
                    return next_url
            except Exception:
                pass

        # Pega o domínio base configurado
        base_domain = getattr(settings, "BASE_DOMAIN", "propzy.com.br")

        # Pega o host da requisição atual
        host = request.get_host().split(":")[0].lower()

        # Verifica se o login foi feito através de um subdomínio
        # (não é o domínio principal nem subdomínios do sistema)
        system_hosts = [
            base_domain,
            f"www.{base_domain}",
            f"app.{base_domain}",
            "localhost",
            "127.0.0.1",
        ]

        is_subdomain = host not in system_hosts and host.endswith(f".{base_domain}")

        # Se foi feito login através de um subdomínio, redireciona para o domínio principal
        if is_subdomain:
            scheme = "https" if request.is_secure() else "http"
            # Usa a URL de redirecionamento padrão do Django
            redirect_path = getattr(settings, "LOGIN_REDIRECT_URL", "/")
            # Se houver um 'next' relativo, usa ele
            if next_url and not next_url.startswith(("http://", "https://")):
                redirect_path = next_url
            redirect_url = f"{scheme}://{base_domain}{redirect_path}"
            return redirect_url

        # Se não for subdomínio, usa o comportamento padrão
        return super().get_login_redirect_url(request)
