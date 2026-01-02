"""
WSGI config for propzy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Força o uso de config.settings, mesmo se já existir uma variável de ambiente
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

application = get_wsgi_application()
