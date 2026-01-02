"""
Configuração do projeto propzy.

Este arquivo garante que o Celery seja carregado quando o Django iniciar.
"""

# Importa o Celery app quando o Django iniciar
from .celery import app as celery_app

__all__ = ("celery_app",)
