#!/usr/bin/env python
"""
Script de teste para DynamicAllowedHosts
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.cache import cache
from apps.landings.models import LandingPage

host = 'orzam.com.br'
cache_key = f'allowed_host:{host}'

print("=" * 60)
print("TESTE DO DynamicAllowedHosts")
print("=" * 60)

# 1. Verificar cache
print(f"\n1. Cache:")
print(f"   Key: {cache_key}")
cached_value = cache.get(cache_key)
print(f"   Value: {cached_value}")

# 2. Verificar no banco
print(f"\n2. Banco de Dados:")
try:
    lp = LandingPage.objects.filter(custom_domain=host).first()
    if lp:
        print(f"   Landing Page encontrada:")
        print(f"     ID: {lp.id}")
        print(f"     Custom Domain: {lp.custom_domain}")
        print(f"     Is Active: {lp.is_active}")
        print(f"     Is Published: {lp.is_published}")

        # Verificar a query .exists()
        is_allowed = LandingPage.objects.filter(
            custom_domain=host,
            is_active=True,
            is_published=True
        ).exists()
        print(f"   Query .exists() result: {is_allowed}")
    else:
        print(f"   ❌ Landing Page NÃO encontrada!")
except Exception as e:
    print(f"   ❌ ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 3. Testar cache.set()
print(f"\n3. Testando cache.set():")
try:
    cache.set(cache_key, True, 300)
    result = cache.get(cache_key)
    print(f"   Salvou True no cache: {result}")

    cache.set(cache_key, False, 300)
    result = cache.get(cache_key)
    print(f"   Salvou False no cache: {result}")
except Exception as e:
    print(f"   ❌ ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 4. Testar DynamicAllowedHosts diretamente
print(f"\n4. Testando DynamicAllowedHosts.__contains__():")
try:
    from django.conf import settings
    
    # Ativar logging detalhado
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('config.dynamic_hosts')
    logger.setLevel(logging.DEBUG)
    
    # Limpar cache antes do teste
    cache.delete(cache_key)
    print(f"   Cache limpo para testar query real...")
    
    # Testar agora
    result = host in settings.ALLOWED_HOSTS
    print(f"   '{host}' in ALLOWED_HOSTS: {result}")
    print(f"   Type: {type(settings.ALLOWED_HOSTS)}")
    
    # Verificar o que foi salvo no cache
    cached_after = cache.get(cache_key)
    print(f"   Cache após teste: {cached_after}")
    
except Exception as e:
    print(f"   ❌ ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

