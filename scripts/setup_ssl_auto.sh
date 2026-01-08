#!/bin/bash

# =============================================================================
# Script de Configuração de SSL Automático para Domínios Personalizados
# =============================================================================
# Configura o sistema para gerar certificados SSL automaticamente
# =============================================================================

set -e

echo "🔐 Configurando SSL Automático para Domínios Personalizados..."

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 1. Criar diretório webroot para Let's Encrypt
echo -e "${CYAN}1/5 - Criando diretório webroot...${NC}"
mkdir -p /var/www/certbot
chmod -R 755 /var/www/certbot
echo -e "${GREEN}✅ Webroot criado: /var/www/certbot${NC}\n"

# 2. Verificar se Certbot está instalado
echo -e "${CYAN}2/5 - Verificando Certbot...${NC}"
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}⚠️  Certbot não encontrado. Instalando...${NC}"
    apt update && apt install certbot -y
fi
echo -e "${GREEN}✅ Certbot instalado: $(certbot --version)${NC}\n"

# 3. Configurar NGINX para acme-challenge
echo -e "${CYAN}3/5 - Configurando NGINX para ACME challenge...${NC}"

# Verificar se já existe a configuração
if ! grep -q "/.well-known/acme-challenge" /opt/propzy/docker/nginx_proxy.conf; then
    echo -e "${YELLOW}⚠️  Adicionando configuração ACME ao NGINX...${NC}"
    echo "
    # ACME Challenge para Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }
    " >> /opt/propzy/docker/nginx_proxy.conf
fi

echo -e "${GREEN}✅ NGINX configurado${NC}\n"

# 4. Configurar Celery Beat para renovação automática
echo -e "${CYAN}4/5 - Configurando renovação automática (Celery Beat)...${NC}"

cat > /tmp/celery_beat_config.py << 'EOF'
# Adicionar ao config/celery.py

from celery.schedules import crontab

# Configuração do Celery Beat
app.conf.beat_schedule = {
    'renew-ssl-certificates-daily': {
        'task': 'apps.landings.tasks.renew_ssl_certificates',
        'schedule': crontab(hour=3, minute=0),  # Todo dia às 3h
    },
}
EOF

echo -e "${GREEN}✅ Configuração Celery Beat criada em /tmp/celery_beat_config.py${NC}"
echo -e "${YELLOW}📝 Adicione o conteúdo ao arquivo config/celery.py${NC}\n"

# 5. Criar cron alternativo (caso Celery não esteja rodando)
echo -e "${CYAN}5/5 - Configurando cron alternativo...${NC}"

# Adicionar ao crontab
CRON_JOB="0 3 * * * docker exec propzy-app python manage.py manage_ssl renew-all >> /var/log/ssl-renew.log 2>&1"

# Verificar se já existe
if ! crontab -l 2>/dev/null | grep -q "manage_ssl renew-all"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo -e "${GREEN}✅ Cron job adicionado${NC}"
else
    echo -e "${GREEN}✅ Cron job já existe${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Configuração concluída!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${CYAN}📋 Próximos passos:${NC}"
echo ""
echo -e "1. ${YELLOW}Reiniciar NGINX:${NC}"
echo -e "   ${CYAN}docker restart propzy-nginx${NC}"
echo ""
echo -e "2. ${YELLOW}Testar geração de certificado:${NC}"
echo -e "   ${CYAN}docker exec propzy-app python manage.py manage_ssl generate --domain seu-dominio.com --email seu@email.com${NC}"
echo ""
echo -e "3. ${YELLOW}Listar certificados:${NC}"
echo -e "   ${CYAN}docker exec propzy-app python manage.py manage_ssl list${NC}"
echo ""
echo -e "4. ${YELLOW}Renovar todos os certificados:${NC}"
echo -e "   ${CYAN}docker exec propzy-app python manage.py manage_ssl renew-all${NC}"
echo ""

echo -e "${CYAN}📚 Como funciona:${NC}"
echo ""
echo -e "  • Quando um cliente adiciona domínio personalizado no Admin"
echo -e "  • Sistema verifica DNS automaticamente (2 min)"
echo -e "  • Gera certificado SSL automaticamente (Let's Encrypt)"
echo -e "  • Renova certificados automaticamente todo dia às 3h"
echo -e "  • Cliente só precisa apontar CNAME para propzy.com.br"
echo ""

echo -e "${GREEN}🎉 Sistema pronto para gerar SSL automaticamente!${NC}"
echo ""














