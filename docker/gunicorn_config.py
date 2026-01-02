"""
Configuração do Gunicorn para produção
Django 5.2 + Celery + propzy
"""

import multiprocessing
import os

# Bind
bind = "0.0.0.0:8000"

# Workers
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "propzy"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Application
chdir = "/app"
wsgi_app = "config.wsgi:application"

# Preload application (melhora performance mas usa mais memória)
preload_app = True


# Server hooks
def on_starting(server):
    """Executado quando o Gunicorn está iniciando"""
    server.log.info("🚀 Gunicorn está iniciando...")


def on_reload(server):
    """Executado quando o Gunicorn recarrega"""
    server.log.info("🔄 Gunicorn está recarregando...")


def when_ready(server):
    """Executado quando o Gunicorn está pronto"""
    server.log.info("✅ Gunicorn está pronto para receber requisições!")


def pre_fork(server, worker):
    """Executado antes de criar um worker"""
    pass


def post_fork(server, worker):
    """Executado após criar um worker"""
    server.log.info(f"👷 Worker {worker.pid} iniciado")


def worker_exit(server, worker):
    """Executado quando um worker sai"""
    server.log.info(f"👋 Worker {worker.pid} encerrado")
