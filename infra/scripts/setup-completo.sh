#!/bin/bash
# Script de Setup Completo e Seguro para VPS
# Execute UMA VEZ na VPS para configurar tudo

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔐 Setup Completo e Seguro - Propzy${NC}"
echo "===================================="
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Execute como root${NC}"
    exit 1
fi

# ============================================
# 1. CONFIGURAR FIREWALL (UFW)
# ============================================
echo -e "${YELLOW}1. Configurando Firewall...${NC}"

# Instalar UFW se não tiver
if ! command -v ufw &> /dev/null; then
    apt update -qq
    apt install -y ufw
fi

# Resetar regras (cuidado!)
ufw --force reset

# Política padrão: DENY tudo
ufw default deny incoming
ufw default allow outgoing

# Permitir SSH (IMPORTANTE - não bloquear você mesmo!)
ufw allow 22/tcp comment 'SSH'

# Permitir HTTP e HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Ativar firewall
ufw --force enable

echo -e "${GREEN}✅ Firewall configurado${NC}"
echo "   Portas abertas: 22 (SSH), 80 (HTTP), 443 (HTTPS)"
echo ""

# ============================================
# 2. INSTALAR DEPENDÊNCIAS
# ============================================
echo -e "${YELLOW}2. Instalando dependências...${NC}"

apt update -qq
apt install -y \
    docker.io \
    docker-compose-plugin \
    git \
    curl \
    certbot \
    python3-certbot-dns-cloudflare \
    ufw \
    fail2ban

# Iniciar Docker
systemctl enable docker
systemctl start docker

echo -e "${GREEN}✅ Dependências instaladas${NC}"
echo ""

# ============================================
# 3. CONFIGURAR FAIL2BAN
# ============================================
echo -e "${YELLOW}3. Configurando Fail2Ban...${NC}"

# Configurar Fail2Ban para SSH
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200
EOF

systemctl enable fail2ban
systemctl restart fail2ban

echo -e "${GREEN}✅ Fail2Ban configurado${NC}"
echo ""

# ============================================
# 4. CONFIGURAR SSH (SEGURANÇA)
# ============================================
echo -e "${YELLOW}4. Configurando SSH...${NC}"

# Backup configuração SSH
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Configurações de segurança SSH
cat >> /etc/ssh/sshd_config << 'EOF'

# Segurança adicional
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

systemctl restart sshd

echo -e "${GREEN}✅ SSH configurado${NC}"
echo ""

# ============================================
# 5. CRIAR ESTRUTURA DE DIRETÓRIOS
# ============================================
echo -e "${YELLOW}5. Criando estrutura de diretórios...${NC}"

mkdir -p /root/apps/propzy
mkdir -p /root/apps/propzy/infra/nginx/ssl
mkdir -p /root/apps/propzy/infra/nginx/certbot
mkdir -p /root/.secrets

chmod 700 /root/.secrets
chmod 755 /root/apps/propzy/infra/nginx/ssl

echo -e "${GREEN}✅ Diretórios criados${NC}"
echo ""

# ============================================
# 6. CONFIGURAR GIT PARA DEPLOY AUTOMÁTICO
# ============================================
echo -e "${YELLOW}6. Configurando Git...${NC}"

# Gerar chave SSH para GitHub Actions
if [ ! -f ~/.ssh/github_actions ]; then
    ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""
    cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/github_actions
    chmod 644 ~/.ssh/authorized_keys
    echo -e "${GREEN}✅ Chave SSH gerada${NC}"
    echo ""
    echo -e "${YELLOW}📋 Adicione esta chave PRIVADA no GitHub Secrets:${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cat ~/.ssh/github_actions
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Chave SSH já existe${NC}"
fi

# Configurar Git
git config --global user.name "Propzy Deploy"
git config --global user.email "deploy@propzy.com.br"

echo -e "${GREEN}✅ Git configurado${NC}"
echo ""

# ============================================
# 7. RESUMO
# ============================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Setup Completo!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📋 Próximos Passos:${NC}"
echo ""
echo "1. Clone o repositório:"
echo "   cd /root/apps/propzy"
echo "   git clone https://github.com/seu-usuario/propzy.git ."
echo ""
echo "2. Configure variáveis de ambiente:"
echo "   cd infra"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "3. Execute deploy:"
echo "   docker compose up -d --build"
echo ""
echo "4. Configure GitHub Secrets:"
echo "   - VPS_SSH_PRIVATE_KEY: (chave mostrada acima)"
echo "   - VPS_IP: 72.60.252.168"
echo ""
echo -e "${GREEN}🎉 Sistema pronto!${NC}"



