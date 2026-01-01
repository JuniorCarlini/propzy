#!/bin/bash
# Script para copiar certificados Let's Encrypt para volume Docker

set -e

CERT_DIR="/etc/letsencrypt/live/propzy.com.br"
DOCKER_CERT_DIR="/root/apps/propzy/infra/nginx/ssl"

# Verificar se certificados existem
if [ ! -f "$CERT_DIR/fullchain.pem" ] || [ ! -f "$CERT_DIR/privkey.pem" ]; then
    echo "❌ Certificados não encontrados em $CERT_DIR"
    exit 1
fi

# Criar diretório se não existir
mkdir -p "$DOCKER_CERT_DIR"

# Copiar certificados
cp "$CERT_DIR/fullchain.pem" "$DOCKER_CERT_DIR/fullchain.pem"
cp "$CERT_DIR/privkey.pem" "$DOCKER_CERT_DIR/privkey.pem"

# Ajustar permissões
chmod 644 "$DOCKER_CERT_DIR/fullchain.pem"
chmod 600 "$DOCKER_CERT_DIR/privkey.pem"

echo "✅ Certificados copiados com sucesso!"
echo "   De: $CERT_DIR"
echo "   Para: $DOCKER_CERT_DIR"



