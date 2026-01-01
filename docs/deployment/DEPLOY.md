# 🚀 Guia de Deploy

## 📋 Pré-requisitos

- VPS com Ubuntu 24.04+
- Acesso root via SSH
- Domínio configurado no Cloudflare

---

## ⚡ Setup Inicial (Uma Vez)

### 1. Conectar na VPS

```bash
ssh root@SEU_IP_VPS
```

### 2. Executar Setup Completo

```bash
# Baixar script de setup
curl -o /tmp/setup.sh https://raw.githubusercontent.com/seu-usuario/propzy/main/infra/scripts/setup-completo.sh

# OU criar manualmente e executar
chmod +x /tmp/setup.sh
/tmp/setup.sh
```

O script configura:
- ✅ Firewall (UFW) - Portas: 22, 80, 443
- ✅ Fail2Ban (proteção SSH)
- ✅ Docker e Docker Compose
- ✅ Certbot (Let's Encrypt)
- ✅ Git e chave SSH para deploy automático
- ✅ Estrutura de diretórios

### 3. Clonar Repositório

```bash
cd /root/apps/propzy
git clone https://github.com/seu-usuario/propzy.git .
```

### 4. Configurar Variáveis de Ambiente

```bash
cd infra
cp .env.example .env
nano .env
```

Configure:
- `SECRET_KEY` (gerar com: `openssl rand -base64 50`)
- `DB_PASSWORD`
- `VPS_IP`
- `PROXY_DOMAIN`
- `CERTBOT_EMAIL`

### 5. Deploy Inicial

```bash
cd infra
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py create_groups
```

### 6. Configurar SSL (Let's Encrypt)

```bash
# Gerar certificado wildcard
certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
  -d propzy.com.br \
  -d "*.propzy.com.br" \
  --email seu-email@exemplo.com \
  --agree-tos \
  --non-interactive

# Copiar certificados
cp /etc/letsencrypt/live/propzy.com.br/fullchain.pem infra/nginx/ssl/
cp /etc/letsencrypt/live/propzy.com.br/privkey.pem infra/nginx/ssl/
chmod 644 infra/nginx/ssl/fullchain.pem
chmod 600 infra/nginx/ssl/privkey.pem

# Reiniciar Nginx
docker compose restart nginx
```

---

## 🔄 Deploy Automático (GitHub Actions)

### Configurar Secrets no GitHub

1. Acesse: `https://github.com/seu-usuario/propzy/settings/secrets/actions`
2. Adicione:
   - `VPS_SSH_PRIVATE_KEY`: Chave privada SSH (gerada no setup)
   - `VPS_IP`: IP da VPS

### Como Funciona

1. **Faça push no GitHub:**
   ```bash
   git add .
   git commit -m "Atualização"
   git push origin main
   ```

2. **Deploy executa automaticamente:**
   - Atualiza código na VPS
   - Reinicia serviços
   - Recarrega Nginx
   - Testa saúde

3. **Verificar no GitHub:**
   - Vá em **Actions**
   - Veja workflow rodando

---

## 🔒 Segurança Configurada

### Firewall (UFW)
- ✅ Porta 22 (SSH) - Aberta
- ✅ Porta 80 (HTTP) - Aberta
- ✅ Porta 443 (HTTPS) - Aberta
- ❌ Todas as outras portas - Bloqueadas

### Fail2Ban
- ✅ Proteção SSH (3 tentativas = ban 2h)
- ✅ Proteção contra brute force

### SSH
- ✅ MaxAuthTries: 3
- ✅ ClientAliveInterval: 300s

---

## 📊 Comandos Úteis

```bash
# Ver status dos serviços
cd /root/apps/propzy/infra
docker compose ps

# Ver logs
docker compose logs -f web

# Reiniciar serviços
docker compose restart web celery celery-beat
docker compose exec nginx nginx -s reload

# Criar superusuário
docker compose exec web python manage.py create_superuser

# Acessar shell Django
docker compose exec web python manage.py shell
```

---

## 🆘 Troubleshooting

### Erro 502 Bad Gateway
```bash
docker compose exec nginx nginx -s reload
```

### Verificar Firewall
```bash
ufw status
ufw allow 22/tcp  # Se bloqueou SSH
```

### Verificar Fail2Ban
```bash
fail2ban-client status sshd
fail2ban-client unban SEU_IP  # Se bloqueou você
```

---

**Sistema configurado com segurança máxima!** 🔐

