#!/bin/bash

# 📋 Script para Ver Logs do Ambiente de Desenvolvimento

set -e

BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================"
echo "📋 Logs - Desenvolvimento"
echo "======================================"
echo -e "${NC}"

# Ver logs de todos os serviços
docker compose -f docker-compose.dev.yml logs -f "$@"

