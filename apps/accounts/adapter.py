# pylint: disable=abstract-method
from typing import Any

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Prevent public signups while keeping admin-created accounts functional."""

    def is_open_for_signup(self, _request: Any) -> bool:
        """Disable the self-service registration flow."""
        return False
