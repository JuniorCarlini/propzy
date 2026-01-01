#!/bin/bash

# 🛑 Script para Parar Ambiente de Desenvolvimento

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}"
echo "======================================"
echo "🛑 Parando Ambiente de Desenvolvimento"
echo "======================================"
echo -e "${NC}"

# Parar containers
docker compose -f docker-compose.dev.yml down

echo ""
echo -e "${RED}✅ Ambiente de desenvolvimento parado${NC}"
echo ""
echo -e "${YELLOW}💡 Para iniciar novamente:${NC}"
echo ""
echo "  ./dev-start.sh"
echo ""

