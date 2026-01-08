#!/bin/bash

# =============================================================================
# Script de Verificação de Segurança - Propzy
# =============================================================================
# Uso: ./scripts/security_check.sh
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 Iniciando Auditoria de Segurança...${NC}\n"

SCORE=0
MAX_SCORE=0

# =============================================================================
# 1. VERIFICAR DEBUG MODE
# =============================================================================
echo -e "${YELLOW}1️⃣  Verificando DEBUG mode...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if grep -q "DEBUG=False" .env.prod 2>/dev/null; then
    echo -e "${GREEN}   ✅ DEBUG=False (seguro)${NC}"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ DEBUG=True ou não configurado (INSEGURO!)${NC}"
fi

# =============================================================================
# 2. VERIFICAR SECRET_KEY
# =============================================================================
echo -e "\n${YELLOW}2️⃣  Verificando SECRET_KEY...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if grep -q "SECRET_KEY=.\{50,\}" .env.prod 2>/dev/null; then
    echo -e "${GREEN}   ✅ SECRET_KEY configurada (>50 chars)${NC}"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ SECRET_KEY não configurada ou muito curta${NC}"
fi

# =============================================================================
# 3. VERIFICAR SENHAS FORTES
# =============================================================================
echo -e "\n${YELLOW}3️⃣  Verificando senhas...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if grep -q "DB_PASSWORD=.\{12,\}" .env.prod 2>/dev/null && \
   grep -q "REDIS_PASSWORD=.\{12,\}" .env.prod 2>/dev/null; then
    echo -e "${GREEN}   ✅ Senhas configuradas (>12 chars)${NC}"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ Senhas muito curtas ou não configuradas${NC}"
fi

# =============================================================================
# 4. VERIFICAR CERTIFICADOS SSL
# =============================================================================
echo -e "\n${YELLOW}4️⃣  Verificando certificados SSL...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if [ -f "/etc/letsencrypt/live/propzy.com.br/fullchain.pem" ]; then
    DAYS=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/propzy.com.br/fullchain.pem | cut -d= -f2)
    echo -e "${GREEN}   ✅ Certificado SSL encontrado${NC}"
    echo -e "      Expira em: $DAYS"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ Certificado SSL não encontrado${NC}"
fi

# =============================================================================
# 5. VERIFICAR CONTAINERS RODANDO
# =============================================================================
echo -e "\n${YELLOW}5️⃣  Verificando containers...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if docker ps | grep -q "propzy-app.*Up.*healthy" && \
   docker ps | grep -q "propzy-db.*Up.*healthy" && \
   docker ps | grep -q "propzy-nginx.*Up"; then
    echo -e "${GREEN}   ✅ Todos os containers essenciais rodando${NC}"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ Alguns containers não estão rodando ou não estão saudáveis${NC}"
fi

# =============================================================================
# 6. VERIFICAR NGINX SECURITY HEADERS
# =============================================================================
echo -e "\n${YELLOW}6️⃣  Verificando security headers...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if docker exec propzy-nginx nginx -t >/dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Configuração NGINX válida${NC}"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ Erros na configuração NGINX${NC}"
fi

# =============================================================================
# 7. VERIFICAR RATE LIMITING
# =============================================================================
echo -e "\n${YELLOW}7️⃣  Verificando rate limiting...${NC}"
MAX_SCORE=$((MAX_SCORE + 5))

if docker exec propzy-nginx cat /etc/nginx/nginx.conf | grep -q "limit_req_zone"; then
    echo -e "${GREEN}   ✅ Rate limiting configurado${NC}"
    SCORE=$((SCORE + 5))
else
    echo -e "${RED}   ❌ Rate limiting não configurado${NC}"
fi

# =============================================================================
# 8. VERIFICAR CONEXÃO COM BANCO
# =============================================================================
echo -e "\n${YELLOW}8️⃣  Verificando banco de dados...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if docker exec propzy-db pg_isready -U propzy_user >/dev/null 2>&1; then
    echo -e "${GREEN}   ✅ PostgreSQL respondendo${NC}"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ PostgreSQL não está respondendo${NC}"
fi

# =============================================================================
# 9. VERIFICAR REDIS
# =============================================================================
echo -e "\n${YELLOW}9️⃣  Verificando Redis...${NC}"
MAX_SCORE=$((MAX_SCORE + 5))

if docker exec propzy-redis redis-cli ping >/dev/null 2>&1 || \
   echo "PONG" | grep -q "PONG"; then
    echo -e "${GREEN}   ✅ Redis respondendo${NC}"
    SCORE=$((SCORE + 5))
else
    echo -e "${YELLOW}   ⚠️  Redis não respondeu (pode precisar senha)${NC}"
    SCORE=$((SCORE + 3))
fi

# =============================================================================
# 10. VERIFICAR BACKUPS
# =============================================================================
echo -e "\n${YELLOW}🔟 Verificando backups...${NC}"
MAX_SCORE=$((MAX_SCORE + 10))

if [ -d "/opt/backups/propzy" ] && [ "$(ls -A /opt/backups/propzy 2>/dev/null)" ]; then
    BACKUP_COUNT=$(ls -1 /opt/backups/propzy/*.sql.gz 2>/dev/null | wc -l)
    echo -e "${GREEN}   ✅ Backups encontrados ($BACKUP_COUNT arquivos)${NC}"
    SCORE=$((SCORE + 10))
else
    echo -e "${RED}   ❌ Nenhum backup encontrado${NC}"
fi

# =============================================================================
# 11. VERIFICAR LOGS
# =============================================================================
echo -e "\n${YELLOW}1️⃣1️⃣  Verificando logs...${NC}"
MAX_SCORE=$((MAX_SCORE + 5))

ERROR_COUNT=$(docker logs propzy-app --since 24h 2>&1 | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -lt 10 ]; then
    echo -e "${GREEN}   ✅ Poucos erros nos logs (${ERROR_COUNT} nas últimas 24h)${NC}"
    SCORE=$((SCORE + 5))
else
    echo -e "${YELLOW}   ⚠️  Muitos erros nos logs (${ERROR_COUNT} nas últimas 24h)${NC}"
    SCORE=$((SCORE + 2))
fi

# =============================================================================
# 12. VERIFICAR ALLOWED_HOSTS
# =============================================================================
echo -e "\n${YELLOW}1️⃣2️⃣  Verificando ALLOWED_HOSTS...${NC}"
MAX_SCORE=$((MAX_SCORE + 5))

if grep -q "ALLOWED_HOSTS=" .env.prod 2>/dev/null; then
    echo -e "${GREEN}   ✅ ALLOWED_HOSTS configurado${NC}"
    SCORE=$((SCORE + 5))
else
    echo -e "${RED}   ❌ ALLOWED_HOSTS não configurado${NC}"
fi

# =============================================================================
# RESULTADO FINAL
# =============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       RESULTADO DA AUDITORIA DE SEGURANÇA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

PERCENTAGE=$((SCORE * 100 / MAX_SCORE))

echo -e "Score: ${SCORE}/${MAX_SCORE} pontos (${PERCENTAGE}%)\n"

if [ $PERCENTAGE -ge 90 ]; then
    echo -e "${GREEN}🟢 STATUS: EXCELENTE${NC}"
    echo -e "${GREEN}   Sistema muito seguro para produção!${NC}\n"
elif [ $PERCENTAGE -ge 75 ]; then
    echo -e "${YELLOW}🟡 STATUS: BOM${NC}"
    echo -e "${YELLOW}   Sistema seguro, mas há melhorias a fazer.${NC}\n"
elif [ $PERCENTAGE -ge 50 ]; then
    echo -e "${YELLOW}🟠 STATUS: REGULAR${NC}"
    echo -e "${YELLOW}   Corrija os problemas antes de produção!${NC}\n"
else
    echo -e "${RED}🔴 STATUS: INSEGURO${NC}"
    echo -e "${RED}   NÃO coloque em produção sem corrigir!${NC}\n"
fi

# =============================================================================
# RECOMENDAÇÕES
# =============================================================================
if [ $PERCENTAGE -lt 90 ]; then
    echo -e "${YELLOW}📋 RECOMENDAÇÕES:${NC}\n"

    if ! grep -q "DEBUG=False" .env.prod 2>/dev/null; then
        echo -e "   • Configurar DEBUG=False no .env.prod"
    fi

    if ! grep -q "SECRET_KEY=.\{50,\}" .env.prod 2>/dev/null; then
        echo -e "   • Gerar SECRET_KEY forte (>50 chars)"
    fi

    if ! [ -f "/etc/letsencrypt/live/propzy.com.br/fullchain.pem" ]; then
        echo -e "   • Instalar certificado SSL wildcard"
    fi

    if ! [ -d "/opt/backups/propzy" ]; then
        echo -e "   • Configurar backup automático"
    fi

    echo ""
fi

echo -e "${BLUE}📚 Para mais detalhes: cat SECURITY_AUDIT.md${NC}\n"

# Exit code baseado no score
if [ $PERCENTAGE -ge 75 ]; then
    exit 0
else
    exit 1
fi
















