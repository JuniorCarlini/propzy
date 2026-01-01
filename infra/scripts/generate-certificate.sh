#!/bin/bash
# Script para gerar certificado Let's Encrypt para novo domínio

set -e

DOMAIN=$1
EMAIL="${CERTBOT_EMAIL:-seu-email@exemplo.com}"

if [ -z "$DOMAIN" ]; then
    echo "❌ Uso: $0 dominio.com.br [email@exemplo.com]"
    exit 1
fi

if [ -n "$2" ]; then
    EMAIL=$2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
INFRA_DIR="$PROJECT_DIR/infra"

echo "🔐 Gerando certificado Let's Encrypt para $DOMAIN..."

# Parar nginx temporariamente
cd "$INFRA_DIR"
echo "⏸️ Parando Nginx..."
docker compose stop nginx

# Gerar certificado
echo "📝 Gerando certificado..."
certbot certonly --standalone \
  -d "$DOMAIN" \
  -d "www.$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --non-interactive

# Copiar certificados (se for propzy.com.br)
if [ "$DOMAIN" = "propzy.com.br" ]; then
    "$SCRIPT_DIR/copy-certificates.sh"
fi

# Reiniciar nginx
echo "▶️ Reiniciando Nginx..."
docker compose start nginx

echo "✅ Certificado gerado com sucesso para $DOMAIN!"
echo "   Certificados salvos em: /etc/letsencrypt/live/$DOMAIN/"



