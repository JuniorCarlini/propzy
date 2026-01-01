#!/bin/bash
# Script para renovar certificados Let's Encrypt e copiar para Docker
# ZERO DOWNTIME - Usa reload ao invés de restart

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
INFRA_DIR="$PROJECT_DIR/infra"

echo "🔄 Iniciando renovação de certificados Let's Encrypt..."

# Renovar certificados
certbot renew --quiet --deploy-hook "$SCRIPT_DIR/copy-certificates.sh"

if [ $? -eq 0 ]; then
    echo "✅ Certificados verificados!"
    
    # Copiar certificados atualizados
    "$SCRIPT_DIR/copy-certificates.sh"
    
    # Recarregar Nginx (ZERO DOWNTIME!)
    cd "$INFRA_DIR"
    docker compose exec nginx nginx -s reload 2>/dev/null || docker compose restart nginx
    
    echo "✅ Renovação concluída e Nginx recarregado (zero downtime)!"
else
    echo "⚠️ Erro na renovação de certificados."
    exit 1
fi

