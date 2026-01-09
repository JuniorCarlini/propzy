#!/bin/bash

# =============================================================================
# Script de Backup - Propzy
# =============================================================================
# Uso: ./scripts/backup.sh
# =============================================================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Diretórios
BACKUP_DIR="/opt/backups/propzy"
DATE=$(date +%Y%m%d_%H%M%S)

echo -e "${YELLOW}📦 Iniciando backup do Propzy...${NC}"

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

# Backup do banco de dados
echo -e "${YELLOW}💾 Fazendo backup do PostgreSQL...${NC}"
docker exec propzy-db pg_dump -U propzy_user propzy_prod | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
echo -e "${GREEN}✅ Backup do banco: $BACKUP_DIR/db_$DATE.sql.gz${NC}"

# Backup de mídia
echo -e "${YELLOW}📁 Fazendo backup dos arquivos de mídia...${NC}"
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /opt/propzy/media/
echo -e "${GREEN}✅ Backup de mídia: $BACKUP_DIR/media_$DATE.tar.gz${NC}"

# Backup do .env.prod
echo -e "${YELLOW}⚙️  Fazendo backup das configurações...${NC}"
cp /opt/propzy/.env.prod "$BACKUP_DIR/env_$DATE.backup"
echo -e "${GREEN}✅ Backup de config: $BACKUP_DIR/env_$DATE.backup${NC}"

# Limpar backups antigos (manter últimos 7 dias)
echo -e "${YELLOW}🧹 Limpando backups antigos...${NC}"
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.backup" -mtime +7 -delete

# Resumo
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Backup concluído com sucesso!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "📍 Localização dos backups: $BACKUP_DIR"
echo ""
ls -lh "$BACKUP_DIR"/*$DATE*
echo ""
echo "💡 Para restaurar:"
echo "   Banco: gunzip < $BACKUP_DIR/db_$DATE.sql.gz | docker exec -i propzy-db psql -U propzy_user propzy_prod"
echo "   Mídia: tar -xzf $BACKUP_DIR/media_$DATE.tar.gz -C /"
echo ""


















