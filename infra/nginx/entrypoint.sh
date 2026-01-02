#!/bin/sh
set -e

echo "🔒 Verificando certificados SSL..."

# Criar diretório de certificados se não existir
mkdir -p /etc/nginx/ssl

# Se certificados Let's Encrypt não existirem, gerar auto-assinados temporários
if [ ! -f /etc/nginx/ssl/fullchain.pem ] || [ ! -f /etc/nginx/ssl/privkey.pem ]; then
    echo "⚠️  Certificados Let's Encrypt não encontrados!"
    echo "📝 Gerando certificados auto-assinados temporários..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/privkey.pem \
        -out /etc/nginx/ssl/fullchain.pem \
        -subj "/C=BR/ST=State/L=City/O=Propzy/CN=propzy.com.br" \
        2>/dev/null
    
    echo "✅ Certificados auto-assinados gerados!"
    echo "⚠️  ATENÇÃO: Estes são certificados temporários. Configure Let's Encrypt para produção!"
else
    echo "✅ Certificados Let's Encrypt encontrados!"
fi

# Verificar configuração do Nginx
echo "🔍 Verificando configuração do Nginx..."
nginx -t

echo "✅ Nginx pronto para iniciar!"

# Executar comando original
exec "$@"

