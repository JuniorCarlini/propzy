#!/bin/bash

# =============================================================================
# Script de Setup para Auto-Scaling com Docker Swarm
# =============================================================================
# Uso: ./scripts/setup_autoscaling.sh
# =============================================================================

set -e

echo "🚀 Configurando Auto-Scaling com Docker Swarm..."

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Verificar se Docker Swarm está ativo
if ! docker info | grep -q "Swarm: active"; then
    echo -e "${YELLOW}⚠️  Docker Swarm não está ativo. Inicializando...${NC}"
    docker swarm init
    echo -e "${GREEN}✅ Swarm inicializado!${NC}\n"
else
    echo -e "${GREEN}✅ Swarm já está ativo!${NC}\n"
fi

# Criar rede overlay se não existir
if ! docker network ls | grep -q "propzy-network"; then
    echo -e "${CYAN}🌐 Criando rede overlay...${NC}"
    docker network create --driver overlay --attachable propzy-network
else
    echo -e "${GREEN}✅ Rede overlay já existe!${NC}"
fi

# Criar stack compose para Swarm
echo -e "${CYAN}📝 Criando configuração do Swarm...${NC}"
cat > docker-compose.swarm.yml << 'EOF'
version: '3.8'

services:
  app:
    image: propzy-app:latest
    build:
      context: .
      dockerfile: docker/Dockerfile.prod
    networks:
      - propzy-network
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
    env_file:
      - .env.prod
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles
    deploy:
      mode: replicated
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      rollback_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  celery_worker:
    image: propzy-app:latest
    command: celery -A config worker -l info
    networks:
      - propzy-network
    env_file:
      - .env.prod
    volumes:
      - ./media:/app/media
    deploy:
      mode: replicated
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  db:
    image: postgres:17-alpine
    networks:
      - propzy-network
    env_file:
      - .env.prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      placement:
        constraints:
          - node.role == manager

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - propzy-network
    volumes:
      - redis_data:/data
    deploy:
      placement:
        constraints:
          - node.role == manager

  nginx-proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx_proxy.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
    networks:
      - propzy-network
    deploy:
      placement:
        constraints:
          - node.role == manager

networks:
  propzy-network:
    external: true

volumes:
  postgres_data:
  redis_data:
EOF

echo -e "${GREEN}✅ Configuração criada!${NC}\n"

# Build da imagem
echo -e "${CYAN}🔨 Fazendo build da imagem...${NC}"
docker build -t propzy-app:latest -f docker/Dockerfile.prod .

# Deploy da stack
echo -e "${CYAN}🚀 Fazendo deploy da stack...${NC}"
docker stack deploy -c docker-compose.swarm.yml propzy

echo -e "${GREEN}✅ Stack deployada!${NC}\n"

# Aguardar serviços iniciarem
echo -e "${CYAN}⏳ Aguardando serviços iniciarem (60s)...${NC}"
sleep 60

# Verificar status
echo -e "${CYAN}📊 Status dos serviços:${NC}"
docker stack services propzy

echo ""
echo -e "${GREEN}🎉 Auto-scaling configurado com sucesso!${NC}\n"

echo -e "${YELLOW}📝 Informações:${NC}"
echo -e "   - Réplicas do App: ${CYAN}2 (mínimo)${NC}"
echo -e "   - Réplicas do Celery: ${CYAN}2 (mínimo)${NC}"
echo -e "   - Load Balancer: ${CYAN}Automático (Docker Swarm)${NC}"
echo -e "   - Health Checks: ${CYAN}Ativados${NC}"

echo ""
echo -e "${YELLOW}🔧 Comandos úteis:${NC}"
echo -e "   Ver serviços: ${CYAN}docker stack services propzy${NC}"
echo -e "   Escalar app: ${CYAN}docker service scale propzy_app=5${NC}"
echo -e "   Ver logs: ${CYAN}docker service logs propzy_app -f${NC}"
echo -e "   Remover stack: ${CYAN}docker stack rm propzy${NC}"

echo ""
echo -e "${YELLOW}💡 Para monitoramento avançado:${NC}"
echo -e "   1. Configure Prometheus: ${CYAN}monitoring/prometheus.yml${NC}"
echo -e "   2. Acesse Grafana (se configurado): ${CYAN}http://servidor:3000${NC}"

echo ""
echo -e "${GREEN}✅ Sistema pronto para auto-scaling!${NC}\n"
