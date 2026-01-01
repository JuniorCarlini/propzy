#!/bin/bash

# 🚀 Script de Início Rápido para Desenvolvimento Local

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================"
echo "🚀 Propzy - Desenvolvimento Local"
echo "======================================"
echo -e "${NC}"

# 1. Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker não está rodando. Inicie o Docker Desktop e tente novamente.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker está rodando${NC}"

# Mudar para diretório infra/dev
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT/infra/dev" || exit 1

# 2. Parar containers antigos (se existirem)
echo ""
echo -e "${YELLOW}🛑 Parando containers anteriores...${NC}"
docker compose -f docker-compose.dev.yml down 2>/dev/null || true

# 3. Construir imagens
echo ""
echo -e "${YELLOW}🔨 Construindo imagens...${NC}"
docker compose -f docker-compose.dev.yml build --no-cache

# 4. Subir serviços
echo ""
echo -e "${YELLOW}🚀 Iniciando serviços...${NC}"
docker compose -f docker-compose.dev.yml up -d

# 5. Aguardar serviços ficarem prontos
echo ""
echo -e "${YELLOW}⏳ Aguardando serviços ficarem prontos...${NC}"
sleep 10

# 6. Executar migrações
echo ""
echo -e "${YELLOW}🔄 Executando migrações...${NC}"
docker compose -f docker-compose.dev.yml exec -T web python manage.py migrate

# 7. Criar superusuário (se não existir)
echo ""
echo -e "${YELLOW}👤 Criando superusuário...${NC}"
docker compose -f docker-compose.dev.yml exec -T web python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@propzy.local').exists():
    User.objects.create_superuser(
        email='admin@propzy.local',
        password='admin123',
        first_name='Admin',
        last_name='Propzy'
    )
    print('✅ Superusuário criado')
else:
    print('✅ Superusuário já existe')
PYTHON

# 8. Criar grupos padrão
echo ""
echo -e "${YELLOW}👥 Criando grupos padrão...${NC}"
docker compose -f docker-compose.dev.yml exec -T web python manage.py create_groups

# 9. Coletar arquivos estáticos
echo ""
echo -e "${YELLOW}📦 Coletando arquivos estáticos...${NC}"
docker compose -f docker-compose.dev.yml exec -T web python manage.py collectstatic --noinput

# 10. Mostrar status
echo ""
echo -e "${GREEN}"
echo "======================================"
echo "✅ Ambiente pronto!"
echo "======================================"
echo -e "${NC}"
echo ""
echo -e "${BLUE}📍 URLs de Acesso:${NC}"
echo ""
echo "  🌐 Aplicação:       http://localhost:8001"
echo "  🔐 Admin:           http://localhost:8001/admin/"
echo "  📧 MailHog:         http://localhost:8026"
echo "  🗄️  PostgreSQL:      localhost:5433"
echo "  📦 Redis:           localhost:6380"
echo ""
echo -e "${BLUE}👤 Credenciais Admin:${NC}"
echo ""
echo "  Email:    admin@propzy.local"
echo "  Senha:    admin123"
echo ""
echo -e "${BLUE}📋 Comandos Úteis:${NC}"
echo ""
echo "  Ver logs:           cd infra/dev && docker compose -f docker-compose.dev.yml logs -f"
echo "  Ver logs (web):     cd infra/dev && docker compose -f docker-compose.dev.yml logs -f web"
echo "  Parar:              cd infra/dev && docker compose -f docker-compose.dev.yml down"
echo "  Reiniciar:          cd infra/dev && docker compose -f docker-compose.dev.yml restart"
echo "  Shell Django:       cd infra/dev && docker compose -f docker-compose.dev.yml exec web python manage.py shell"
echo "  Criar migração:     cd infra/dev && docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations"
echo "  Aplicar migração:   cd infra/dev && docker compose -f docker-compose.dev.yml exec web python manage.py migrate"
echo ""
echo -e "${GREEN}✨ Bom desenvolvimento!${NC}"
echo ""

