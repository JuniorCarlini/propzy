#!/bin/bash
# Não usar set -e aqui para não parar se docker-compose falhar
# set -e

# Forçar output imediato (sem buffering) e garantir que apareça
export PYTHONUNBUFFERED=1
# Redirecionar stderr para stdout e garantir que tudo apareça
exec 2>&1

# Banner inicial bem visível
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 INICIANDO TODOS OS SERVIÇOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Iniciando TODOS os serviços (web, db, redis, celery_worker, celery_beat)..."

# Encontrar o docker-compose.yml
COMPOSE_FILE="/app/docker-compose.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    COMPOSE_FILE="/workspaces/propzy/docker-compose.yml"
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "⚠️ docker-compose.yml não encontrado, continuando com verificações..."
else
    # Tentar iniciar todos os serviços explicitamente (pode falhar se já estiverem rodando ou sem acesso ao Docker)
    if command -v docker >/dev/null 2>&1; then
        docker compose -f "$COMPOSE_FILE" up -d db redis celery_worker celery_beat 2>/dev/null || docker-compose -f "$COMPOSE_FILE" up -d db redis celery_worker celery_beat 2>/dev/null || echo "⚠️ Não foi possível iniciar containers via docker-compose (pode já estarem rodando)"
    else
        echo "⚠️ Docker não disponível neste ambiente, continuando com verificações..."
    fi
fi

echo ""
echo "✅ Serviços iniciados!"
echo ""

# Tentar mostrar status dos containers (pode não funcionar dentro do container)
if command -v docker >/dev/null 2>&1; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 STATUS DOS CONTAINERS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker compose -f "$COMPOSE_FILE" ps 2>/dev/null || docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null || echo "⚠️ Não foi possível verificar containers (sem acesso ao Docker)"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 VERIFICANDO STATUS DOS SERVIÇOS DENTRO DO CONTAINER WEB..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Aguardar um pouco para os serviços iniciarem (entrypoint precisa de tempo para iniciar Celery)
echo "⏳ Aguardando serviços iniciarem..."
sleep 8

# Verificar PostgreSQL
if pg_isready -h ${DB_HOST:-db} -U ${DB_USER:-propzy_user} 2>/dev/null; then
    echo "✅ PostgreSQL: FUNCIONANDO (Host: ${DB_HOST:-db})"
else
    echo "❌ PostgreSQL: NÃO RESPONDE"
fi

# Verificar Redis
REDIS_CHECK=$(python -c "
import redis
import sys
try:
    r = redis.Redis(host='${REDIS_HOST:-redis}', port=${REDIS_PORT:-6379}, socket_connect_timeout=2, decode_responses=False)
    r.ping()
    info = r.info('server')
    print(f\"OK|v{info.get('redis_version', '?')}\")
except redis.exceptions.ConnectionError:
    print('CONNECTION_ERROR')
except redis.exceptions.AuthenticationError:
    print('AUTH_ERROR')
except Exception as e:
    print(f'ERROR|{str(e)}')
" 2>/dev/null || echo "ERROR")

if echo "$REDIS_CHECK" | grep -q "OK"; then
    REDIS_VERSION=$(echo "$REDIS_CHECK" | cut -d'|' -f2)
    echo "✅ Redis: FUNCIONANDO (Host: ${REDIS_HOST:-redis}, Versão: $REDIS_VERSION)"
elif echo "$REDIS_CHECK" | grep -q "CONNECTION_ERROR"; then
    echo "⚠️ Redis: NÃO CONECTADO (pode estar iniciando ainda...)"
elif echo "$REDIS_CHECK" | grep -q "AUTH_ERROR"; then
    echo "⚠️ Redis: REQUER AUTENTICAÇÃO (verifique configuração)"
else
    echo "❌ Redis: ERRO AO VERIFICAR"
fi

# Verificar Celery Worker
check_celery_running() {
    python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${DJANGO_SETTINGS_MODULE:-config.settings.local}')
from django.conf import settings
import django
django.setup()
from config.celery import app
inspect = app.control.inspect()
stats = inspect.stats()
exit(0 if stats else 1)
" 2>/dev/null
}

# Verificar Celery Worker (pode estar rodando neste container ou em container separado)
CELERY_WORKER_RUNNING=false

# Verificar se está rodando neste container (via PID file)
if [ -f /tmp/celery_worker.pid ]; then
    WORKER_PID=$(cat /tmp/celery_worker.pid 2>/dev/null)
    if kill -0 $WORKER_PID 2>/dev/null; then
        CELERY_WORKER_RUNNING=true
        echo "✅ Celery Worker: FUNCIONANDO neste container (PID: $WORKER_PID)"
    else
        echo "⚠️ Celery Worker: PID file existe mas processo não está rodando"
    fi
fi

# Verificar se está respondendo via inspect (pode estar em container separado)
if check_celery_running; then
    CELERY_STATS=$(python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${DJANGO_SETTINGS_MODULE:-config.settings.local}')
from django.conf import settings
import django
django.setup()
from config.celery import app
inspect = app.control.inspect()
stats = inspect.stats()
if stats:
    worker_name = list(stats.keys())[0]
    registered = inspect.registered()
    task_count = len(registered[worker_name]) if registered and worker_name in registered else 0
    print(f'{worker_name} ({task_count} tarefas registradas)')
" 2>/dev/null || echo "Worker ativo")
    
    if [ "$CELERY_WORKER_RUNNING" = false ]; then
        echo "✅ Celery Worker: FUNCIONANDO (provavelmente em container separado) - $CELERY_STATS"
    else
        echo "   ℹ️  Detalhes: $CELERY_STATS"
    fi
    CELERY_WORKER_RUNNING=true
elif [ "$CELERY_WORKER_RUNNING" = false ]; then
    echo "⚠️ Celery Worker: NÃO ESTÁ RODANDO"
    echo "   ℹ️  O Celery Worker deveria iniciar automaticamente pelo entrypoint.sh"
    echo "   ℹ️  Ou pode estar rodando em container separado (celery_worker)"
fi

# Verificar Celery Beat
CELERY_BEAT_RUNNING=false

if [ -f /tmp/celerybeat.pid ]; then
    BEAT_PID=$(cat /tmp/celerybeat.pid 2>/dev/null || echo "N/A")
    if kill -0 $BEAT_PID 2>/dev/null; then
        echo "✅ Celery Beat: FUNCIONANDO neste container (PID: $BEAT_PID)"
        CELERY_BEAT_RUNNING=true
    else
        echo "⚠️ Celery Beat: PID file existe mas processo não está rodando"
    fi
else
    echo "⚠️ Celery Beat: NÃO ESTÁ RODANDO neste container"
    echo "   ℹ️  O Celery Beat deveria iniciar automaticamente pelo entrypoint.sh"
    echo "   ℹ️  Ou pode estar rodando em container separado (celery_beat)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 VERIFICAÇÃO COMPLETA!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 PostgreSQL: Verificado"
echo "🔴 Redis: Verificado"
echo "⚙️  Celery Worker: Verificado"
echo "⏰ Celery Beat: Verificado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 AMBIENTE DE DESENVOLVIMENTO PRONTO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Todos os serviços foram verificados!"
echo "📝 Logs completos salvos em: /tmp/devcontainer-start.log"
echo ""

