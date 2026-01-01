#!/bin/bash
set -e

echo "🚀 Iniciando Celery Beat..."

# Aguardar Redis estar pronto (usando Python para verificar)
echo "⏳ Aguardando Redis..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if python -c "import redis; r = redis.Redis(host='${REDIS_HOST:-redis}', port=${REDIS_PORT:-6379}, socket_connect_timeout=1); r.ping()" 2>/dev/null; then
        echo "✅ Redis está pronto!"
        break
    fi
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Timeout aguardando Redis"
        exit 1
    fi
    sleep 1
done

# Iniciar Celery Beat
echo "⏰ Iniciando Celery Beat..."
exec celery -A config.celery beat \
    --loglevel=info \
    --pidfile=/tmp/celerybeat.pid

