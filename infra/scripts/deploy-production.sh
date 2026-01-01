#!/bin/bash
# Script de deploy para produção na VPS

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Iniciando deploy em produção...${NC}"
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Erro: docker-compose.yml não encontrado!${NC}"
    echo "Execute este script a partir do diretório infra/"
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Erro: Arquivo .env não encontrado!${NC}"
    echo "Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# Verificar se DEBUG está como False
if grep -q "DEBUG=True" .env; then
    echo -e "${YELLOW}⚠️  AVISO: DEBUG está como True no .env${NC}"
    echo "Em produção, DEBUG deve ser False!"
    read -p "Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Parar containers existentes
echo -e "${YELLOW}⏹️  Parando containers existentes...${NC}"
docker compose down

# Construir imagens
echo -e "${YELLOW}🔨 Construindo imagens...${NC}"
docker compose build --no-cache

# Subir serviços
echo -e "${YELLOW}⬆️  Subindo serviços...${NC}"
docker compose up -d

# Aguardar serviços estarem prontos
echo -e "${YELLOW}⏳ Aguardando serviços estarem prontos...${NC}"
sleep 15

# Executar migrações
echo -e "${YELLOW}📦 Executando migrações...${NC}"
docker compose exec -T web python manage.py migrate --noinput

# Coletar arquivos estáticos
echo -e "${YELLOW}📁 Coletando arquivos estáticos...${NC}"
docker compose exec -T web python manage.py collectstatic --noinput

# Criar grupos padrão
echo -e "${YELLOW}👥 Criando grupos padrão...${NC}"
docker compose exec -T web python manage.py create_groups || echo "Grupos já existem"

# Verificar status dos serviços
echo -e "${YELLOW}📊 Status dos serviços:${NC}"
docker compose ps

# Verificar saúde dos serviços
echo ""
echo -e "${YELLOW}🏥 Verificando saúde dos serviços...${NC}"
if docker compose ps | grep -q "unhealthy"; then
    echo -e "${RED}⚠️  Alguns serviços estão unhealthy!${NC}"
    docker compose ps
else
    echo -e "${GREEN}✅ Todos os serviços estão saudáveis${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo -e "${BLUE}📍 Próximos passos:${NC}"
echo -e "   1. Criar tenant e domínio:"
echo -e "      ${YELLOW}docker compose exec web python manage.py shell${NC}"
echo ""
echo -e "   2. Criar superusuário:"
echo -e "      ${YELLOW}docker compose exec web python manage.py create_superuser${NC}"
echo ""
echo -e "   3. Verificar logs:"
echo -e "      ${YELLOW}docker compose logs -f${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"



