#!/bin/bash
set -e

echo "🚀 Iniciando configuração do Django..."

# Função para aguardar o banco de dados
wait_for_db() {
    echo "⏳ Aguardando conexão com o banco de dados..."

    # Extrai configurações do DATABASE_URL ou variáveis de ambiente
    if [ -n "$DATABASE_URL" ]; then
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
        DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*\/\/[^:]*:\([^@]*\)@.*/\1/p')
        DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    else
        DB_HOST=${DB_HOST:-db}
        DB_PORT=${DB_PORT:-5432}
        DB_USER=${DB_USER:-propzy}
        DB_PASS=${DB_PASSWORD:-propzy123}
        DB_NAME=${DB_NAME:-propzy}
    fi

    echo "📋 Configurações do banco:"
    echo "   Host: $DB_HOST"
    echo "   Porta: $DB_PORT"
    echo "   Usuário: $DB_USER"
    echo "   Banco: $DB_NAME"

    # Aguarda até que o PostgreSQL esteja disponível
    until python << END
import psycopg2
import sys
try:
    conn = psycopg2.connect(
        host="$DB_HOST",
        port="$DB_PORT",
        user="$DB_USER",
        password="$DB_PASS",
        dbname="$DB_NAME"
    )
    conn.close()
    print("✅ Banco de dados conectado!")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)
END
    do
        echo "⏳ Banco ainda não está pronto. Aguardando 2 segundos..."
        sleep 2
    done
}

# Função para executar migrações
run_migrations() {
    echo "🔄 Executando migrações do banco de dados..."
    python manage.py migrate --noinput

    if [ $? -eq 0 ]; then
        echo "✅ Migrações executadas com sucesso!"
    else
        echo "❌ Erro ao executar migrações!"
        exit 1
    fi
}

# Função para coletar arquivos estáticos
collect_static() {
    echo "📦 Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput

    if [ $? -eq 0 ]; then
        echo "✅ Arquivos estáticos coletados!"
    else
        echo "⚠️  Aviso: Erro ao coletar arquivos estáticos (não crítico)"
    fi
}

compile_messages() {
    if [ -d "locale" ]; then
        echo "🌐 Compilando traduções..."
        # Verifica se o utilitário msgfmt (parte do gettext) está disponível na imagem
        if command -v msgfmt >/dev/null 2>&1; then
            if python manage.py compilemessages; then
                echo "✅ Traduções compiladas!"
            else
                echo "⚠️  Aviso: Erro ao compilar traduções (verifique permissões/dependências)"
            fi
        else
            echo "⚠️  Ignorando compilação: utilitário 'msgfmt' não encontrado (gettext não instalado na imagem)."
            echo "   Para habilitar a compilação automática, instale gettext na imagem (ex.: apt-get update && apt-get install -y gettext) e reconstrua o container."
        fi
    else
        echo "ℹ️  Diretório de traduções inexistente, pulando compilação..."
    fi
}

# Função para criar superusuário se não existir
create_superuser() {
    if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo "👤 Verificando/criando superusuário..."
        python manage.py shell <<'END'
import os
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
username = os.environ.get("DJANGO_SUPERUSER_USERNAME") or email

username_field = User.USERNAME_FIELD
lookup_field = username_field if username_field != "email" else "email"
lookup_value = username if username_field != "email" else email

if not lookup_value:
    raise ValueError("A variável de ambiente para identificar o superusuário está ausente.")

if not User.objects.filter(**{lookup_field: lookup_value}).exists():
    create_kwargs = {"email": email, username_field: lookup_value}
    try:
        User.objects.create_superuser(password=password, **create_kwargs)
        print(f"✅ Superusuário '{lookup_value}' criado!")
    except IntegrityError as exc:  # pragma: no cover - somente informativo
        print(f"❌ Não foi possível criar o superusuário: {exc}")
else:
    print(f"👤 Superusuário '{lookup_value}' já existe!")
END
    else
        echo "ℹ️  Variáveis de superusuário não definidas, pulando criação..."
    fi
}

# Execução principal
main() {
    echo "🚀 ====== INICIANDO SETUP DO DJANGO ======"

    # Aguarda banco de dados
    wait_for_db

    # Executa configurações do Django
    run_migrations
    collect_static
    compile_messages
    create_superuser

    echo "✅ ====== SETUP CONCLUÍDO! ======"

    # Se o comando for "supervisord", inicia o supervisord
    if [ "$1" = "supervisord" ]; then
        echo "🚀 Iniciando Supervisord..."
        exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
    else
        echo "🚀 Executando comando: $@"
        exec "$@"
    fi
}

# Executa a função principal com todos os argumentos
main "$@"
