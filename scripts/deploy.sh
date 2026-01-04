#!/bin/bash

# =============================================================================
# Script de Deploy Simplificado - Propzy
# =============================================================================
# Uso: ./scripts/deploy.sh
# =============================================================================

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do Propzy..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Erro: docker-compose.prod.yml não encontrado!${NC}"
    echo "Execute este script do diretório raiz do projeto."
    exit 1
fi

# Verificar se .env.prod existe
if [ ! -f ".env.prod" ]; then
    echo -e "${RED}❌ Erro: .env.prod não encontrado!${NC}"
    echo "Copie .env.prod.example para .env.prod e configure as variáveis."
    exit 1
fi

echo -e "${CYAN}📦 1/7 - Verificando containers...${NC}"
docker-compose -f docker-compose.prod.yml ps

echo -e "${CYAN}🔨 2/7 - Build das imagens...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

echo -e "${CYAN}🚀 3/7 - Iniciando serviços...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo -e "${CYAN}⏳ Aguardando containers iniciarem (30s)...${NC}"
sleep 30

echo -e "${CYAN}🗄️  4/7 - Executando migrations...${NC}"
docker exec propzy-app python manage.py migrate --noinput

echo -e "${CYAN}📁 5/7 - Coletando arquivos estáticos...${NC}"
docker exec propzy-app python manage.py collectstatic --noinput

echo -e "${CYAN}🎨 6/7 - Instalando temas...${NC}"
docker exec propzy-app python manage.py install_themes

echo -e "${CYAN}✅ 7/7 - Verificando saúde dos containers...${NC}"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}\n"

echo -e "${CYAN}📊 Status dos Serviços:${NC}"
docker ps --filter "name=propzy-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo -e "   1. Criar superusuário: ${CYAN}docker exec -it propzy-app python manage.py createsuperuser${NC}"
echo -e "   2. Acessar admin: ${CYAN}https://seu-dominio.com.br/admin/${NC}"
echo -e "   3. Criar landing pages no admin"
echo -e "   4. Testar subdomínios: ${CYAN}https://usuario.seu-dominio.com.br${NC}"

echo ""
echo -e "${YELLOW}🔧 Comandos úteis:${NC}"
echo -e "   Ver logs: ${CYAN}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "   Reiniciar: ${CYAN}docker-compose -f docker-compose.prod.yml restart${NC}"
echo -e "   Parar tudo: ${CYAN}docker-compose -f docker-compose.prod.yml down${NC}"

echo ""
echo -e "${CYAN}📚 Documentação:${NC}"
echo -e "   DEPLOY.md           - Guia completo de deploy"
echo -e "   SECURITY_SUMMARY.md - Auditoria de segurança"
echo -e "   LANDINGS_README.md  - Documentação técnica"

echo ""
echo -e "${GREEN}🎉 Sistema pronto para uso!${NC}\n"
