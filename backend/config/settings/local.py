"""
Django settings for propzy project - Local Development
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Security settings relaxadas para desenvolvimento
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Email backend para desenvolvimento
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug Toolbar (opcional)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass



