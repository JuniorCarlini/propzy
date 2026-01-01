"""
Django settings for propzy project - Production
"""
from .base import *

DEBUG = False

# SECRET_KEY obrigatória em produção
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY environment variable is required in production!")

# ALLOWED_HOSTS mais restritivo (confia no middleware para validação adicional)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else []

# CSRF Trusted Origins - Domínios permitidos para CSRF
# Busca dinamicamente domínios verificados do banco de dados
def get_csrf_trusted_origins():
    """
    Retorna lista de CSRF Trusted Origins incluindo:
    1. Domínios padrão (propzy.com.br e subdomínios)
    2. Domínios verificados do banco de dados (dinâmico)
    """
    # Domínios padrão sempre incluídos
    default_origins = [
        'https://propzy.com.br',
        'https://app.propzy.com.br',
        'https://*.propzy.com.br',
    ]
    
    # Tentar buscar domínios verificados do banco
    try:
        # Verificar se apps estão carregados
        from django.apps import apps
        if apps.is_installed('apps.domains'):
            from apps.domains.models import Domain
            
            # Buscar todos os domínios verificados
            verified_domains = Domain.objects.filter(is_verified=True).values_list('domain', flat=True)
            
            # Adicionar domínios verificados com https://
            for domain in verified_domains:
                origin = f'https://{domain}'
                if origin not in default_origins:
                    default_origins.append(origin)
    except Exception:
        # Se houver erro (apps não carregados, banco não disponível, etc)
        # Usar apenas domínios padrão
        pass
    
    # Verificar variável de ambiente (sobrescreve tudo se definida)
    env_origins = os.environ.get('CSRF_TRUSTED_ORIGINS')
    if env_origins:
        return env_origins.split(',')
    
    return default_origins

CSRF_TRUSTED_ORIGINS = get_csrf_trusted_origins()

# Security settings rigorosas para produção
SECURE_SSL_REDIRECT = True  # Origin CA instalado - SSL end-to-end
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Database connection pooling otimizado
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Logging otimizado para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django_errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_errors'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

