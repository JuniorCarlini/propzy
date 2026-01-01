#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ INICIANDO CELERY WORKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /app

# Aguardar banco de dados
echo "⏳ Aguardando PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(host='db', dbname='propzy_dev', user='postgres', password='postgres_dev')" 2>/dev/null; do
  echo "   PostgreSQL ainda não está pronto..."
  sleep 2
done
echo "✅ PostgreSQL conectado!"

# Aguardar Redis
echo "⏳ Aguardando Redis..."
until python -c "import redis; r = redis.Redis(host='redis', port=6379, password='redis_dev_password'); r.ping()" 2>/dev/null; do
  echo "   Redis ainda não está pronto..."
  sleep 2
done
echo "✅ Redis conectado!"

# Aguardar Django estar pronto
echo "⏳ Aguardando Django..."
until python -c "import urllib.request; urllib.request.urlopen('http://web:8000/api/health/', timeout=5)" 2>/dev/null; do
  echo "   Django ainda não está pronto..."
  sleep 2
done
echo "✅ Django conectado!"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CELERY WORKER PRONTO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ Worker iniciado com autoscale (4,1)"
echo "📊 Logs de tarefas serão exibidos abaixo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Iniciar Celery Worker
exec celery -A config worker \
  --loglevel=info \
  --autoscale=4,1 \
  --max-tasks-per-child=1000





