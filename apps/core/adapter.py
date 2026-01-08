# pylint: disable=abstract-method
"""
Adapter customizado do django-allauth
"""
from typing import Any

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """
    Adapter que desabilita cadastro público.
    Usuários só podem ser criados por administradores.
    """

    def is_open_for_signup(self, _request: Any) -> bool:
        """Desabilita o fluxo de auto-registro."""
        return False
















