#!/usr/bin/env python
"""
Script para testar DynamicAllowedHosts
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
import logging

# Ativar logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

host = 'orzam.com.br'

print("=" * 60)
print("TESTE DETALHADO DO __contains__()")
print("=" * 60)

# Limpar cache
cache_key = f'allowed_host:{host}'
cache.delete(cache_key)
print(f"\n1. Cache limpo para '{host}'")

# Testar
print(f"\n2. Testando: '{host}' in ALLOWED_HOSTS")
print(f"   Type: {type(settings.ALLOWED_HOSTS)}")
print(f"   Base hosts: {settings.ALLOWED_HOSTS.base_hosts}")

try:
    result = host in settings.ALLOWED_HOSTS
    print(f"   Resultado: {result}")
except Exception as e:
    print(f"   ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Verificar cache após teste
cached = cache.get(cache_key)
print(f"\n3. Cache após teste: {cached}")

# Verificar no banco
print(f"\n4. Verificar no banco de dados:")
try:
    from apps.landings.models import LandingPage
    lp = LandingPage.objects.filter(custom_domain=host, is_active=True, is_published=True).first()
    if lp:
        print(f"   ✅ Landing Page encontrada: ID={lp.id}")
    else:
        print(f"   ❌ Landing Page NÃO encontrada")
except Exception as e:
    print(f"   ❌ Erro ao consultar banco: {type(e).__name__}: {e}")

print("\n" + "=" * 60)

