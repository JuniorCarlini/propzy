#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 INICIANDO DJANGO WEB SERVER"
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

# Migrations
echo "📦 Executando migrations..."
python manage.py migrate --noinput
echo "✅ Migrations concluídas!"

# Collectstatic (se necessário)
if [ ! -f /app/staticfiles/.collectstatic.done ]; then
  echo "📦 Coletando arquivos estáticos..."
  python manage.py collectstatic --noinput || true
  touch /app/staticfiles/.collectstatic.done
  echo "✅ Arquivos estáticos coletados!"
fi

# Criar tenant padrão e superusuário se necessário
echo "👤 Verificando tenant padrão e superusuário..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant

User = get_user_model()

# Criar ou obter tenant padrão
tenant, created = Tenant.objects.get_or_create(
    slug='default',
    defaults={
        'name': 'Tenant Padrão',
        'is_active': True,
    }
)
if created:
    print(f'✅ Tenant padrão criado: {tenant.name}')

# Criar superusuário se não existir
if not User.objects.filter(email='admin@propzy.local', tenant=tenant).exists():
    User.objects.create_superuser('admin@propzy.local', 'admin123', tenant=tenant)
    print('✅ Superusuário criado: admin@propzy.local / admin123')
else:
    print('ℹ️  Superusuário já existe')
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DJANGO WEB SERVER PRONTO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Acesse: http://localhost:8000"
echo "👤 Login: admin@propzy.local / admin123"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Iniciar servidor de desenvolvimento
exec python manage.py runserver 0.0.0.0:8000





