#!/bin/bash
set -e

echo "🚀 Iniciando entrypoint..."

# Aguardar PostgreSQL estar pronto
echo "⏳ Aguardando PostgreSQL..."
while ! pg_isready -h $DB_HOST -U $DB_USER; do
    sleep 1
done
echo "✅ PostgreSQL está pronto!"

# Criar migrations se necessário
echo "📝 Criando migrations..."
python manage.py makemigrations --noinput || echo "⚠️ Nenhuma migration nova para criar"

# Executar migrações
echo "📦 Executando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar grupos padrão
echo "👥 Criando grupos padrão..."
python manage.py create_groups || echo "⚠️ Grupos já existem ou comando não encontrado"

# Criar superusuário se não existir (apenas em desenvolvimento)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Criando superusuário..."
    python manage.py createsuperuser --noinput || echo "⚠️ Superusuário já existe"
fi

echo "✅ Entrypoint concluído!"

# Executar comando passado como argumento
exec "$@"
