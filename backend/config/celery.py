"""
Configuração do Celery para processamento assíncrono.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Definir o módulo de configuração padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('propzy')

# Carregar configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobrir tarefas automaticamente em todos os apps Django
app.autodiscover_tasks()

# Configurar tarefas periódicas (Celery Beat)
app.conf.beat_schedule = {
    'verify-pending-domains': {
        'task': 'apps.domains.tasks.verify_all_pending_domains',
        'schedule': crontab(minute='*/30'),  # A cada 30 minutos
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
