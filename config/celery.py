"""
Configuração do Celery para o projeto propzy.

Este arquivo configura o Celery para processar tarefas assíncronas em background,
usando Redis como broker e backend de resultados.
"""

import os

from celery import Celery

# Define o módulo de settings padrão do Django para o Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Cria a instância do Celery
app = Celery("propzy")

# Configura o Celery usando as configurações do Django
# O prefixo 'CELERY_' indica que todas as configurações relacionadas ao Celery
# devem ter esse prefixo no settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descobre automaticamente tarefas em todos os apps instalados
# Procura por arquivos tasks.py em cada app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Tarefa de debug para testar se o Celery está funcionando.
    """
    print(f"Request: {self.request!r}")
