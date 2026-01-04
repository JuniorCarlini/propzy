# 🚀 INSTALAÇÃO COMPLETA DO ZERO - Sistema Propzy

## ✨ Guia Definitivo: VPS Zerada → Sistema Funcionando

Tempo: 60-90 minutos
Dificuldade: ⭐⭐ (Fácil - só seguir os passos)

---

## 📋 PRÉ-REQUISITOS

- [ ] VPS com Ubuntu 22.04+ (limpa/zerada)
- [ ] Domínio registrado (ex: propzy.com.br)
- [ ] Conta Cloudflare (grátis)
- [ ] Acesso SSH (root)
- [ ] Código no GitHub

---

## 🎯 PARTE 1: PREPARAR SERVIDOR (20 min)

### 1.1 Conectar via SSH

```bash
ssh root@SEU_IP_DO_SERVIDOR
```

### 1.2 Atualizar Sistema

```bash
apt update && apt upgrade -y
```

### 1.3 Instalar Docker

```bash
# Download e instalação automática
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verificar
docker --version
# Deve mostrar: Docker version 24.x.x
```

### 1.4 Instalar Docker Compose

```bash
# Instalar
apt install docker-compose-plugin -y

# Verificar
docker compose version
# Deve mostrar: Docker Compose version v2.x.x
```

### 1.5 Instalar Portainer

```bash
# Criar volume
docker volume create portainer_data

# Instalar Portainer CE
docker run -d \
  -p 8000:8000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

# Verificar
docker ps
# Deve mostrar container "portainer" running
```

### 1.6 Acessar Portainer

```
https://SEU_IP:9443
```

**Criar conta admin:**
- Username: admin
- Password: (senha forte - mínimo 12 caracteres)

**Selecionar Environment:** Get Started → local

---

## 🌐 PARTE 2: CONFIGURAR DNS (5 min)

### 2.1 Acessar Cloudflare

```
https://dash.cloudflare.com
```

### 2.2 Adicionar Registros DNS

**Seu domínio** → **DNS** → **Records**

**Adicionar 3 registros:**

#### Registro 1: Domínio Principal
```
Type:    A
Name:    @
Content: SEU_IP_DO_SERVIDOR
Proxy:   ✅ Proxied (laranja)
TTL:     Auto
```

#### Registro 2: Wildcard (CRÍTICO!)
```
Type:    A
Name:    *
Content: SEU_IP_DO_SERVIDOR
Proxy:   ✅ Proxied (laranja)
TTL:     Auto
```

#### Registro 3: WWW
```
Type:    CNAME
Name:    www
Target:  propzy.com.br
Proxy:   ✅ Proxied (laranja)
TTL:     Auto
```

### 2.3 Configurar SSL no Cloudflare

**SSL/TLS** → **Overview** → **Full (strict)**

**SSL/TLS** → **Edge Certificates:**
- ✅ Always Use HTTPS: ON
- ✅ Automatic HTTPS Rewrites: ON

### 2.4 Testar DNS (Via SSH)

```bash
nslookup propzy.com.br
nslookup teste.propzy.com.br
# Ambos devem retornar IPs do Cloudflare (104.x.x.x)
```

---

## 🔐 PARTE 3: GERAR CERTIFICADO SSL WILDCARD (15 min)

### 3.1 Instalar Certbot

```bash
apt install certbot -y
```

### 3.2 Gerar Certificado Wildcard

```bash
certbot certonly --manual --preferred-challenges dns \
  -d propzy.com.br \
  -d *.propzy.com.br \
  --agree-tos \
  --email seu-email@exemplo.com
```

### 3.3 Adicionar Registros TXT (Cloudflare)

**Certbot vai pedir 2 registros TXT:**

**No Cloudflare:** DNS → Add record

#### Registro TXT 1:
```
Type:    TXT
Name:    _acme-challenge
Content: (valor fornecido pelo Certbot)
Proxy:   🔴 DNS only (cinza)
TTL:     Auto
```

**Aguarde 2 minutos** → Pressione Enter no Certbot

#### Registro TXT 2:
```
Type:    TXT
Name:    _acme-challenge
Content: (segundo valor do Certbot)
Proxy:   🔴 DNS only (cinza)
TTL:     Auto
```

**Aguarde 2 minutos** → Pressione Enter no Certbot

### 3.4 Verificar Certificado

```bash
ls -la /etc/letsencrypt/live/propzy.com.br/
# Deve ter: fullchain.pem e privkey.pem
```

**Depois pode remover os TXT do Cloudflare (já não precisa mais)**

---

## 📂 PARTE 4: PREPARAR DIRETÓRIOS (2 min)

```bash
# Criar estrutura
mkdir -p /opt/propzy
mkdir -p /var/www/certbot
chmod -R 755 /opt/propzy
chmod -R 755 /var/www/certbot

# Verificar
ls -la /opt/
ls -la /var/www/
```

---

## 🔑 PARTE 5: CONFIGURAR GITHUB (5 min)

### 5.1 Criar Token

**GitHub:** https://github.com/settings/tokens

1. **Generate new token** → **Tokens (classic)**
2. **Note:** `Portainer Propzy`
3. **Expiration:** No expiration
4. **Select scopes:**
   - ✅ **repo** (Full control)
5. **Generate token**
6. **COPIAR TOKEN** ⚠️ (guarde em local seguro!)

```
Exemplo: ghp_1234567890abcdefghijklmnopqrstuvwxyzABCD
```

### 5.2 Fazer Commit Final

**No seu computador:**

```bash
cd /caminho/do/projeto

# Adicionar tudo
git add .

# Commit
git commit -m "Deploy production ready"

# Push
git push origin main
```

**Verificar se está no GitHub:**
- Acesse seu repositório
- Verifique se tem todos os arquivos

---

## 🐳 PARTE 6: CRIAR STACK NO PORTAINER (15 min)

### 6.1 Acessar Portainer

```
https://SEU_IP:9443
```

### 6.2 Criar Nova Stack

**Menu:** Stacks → **+ Add stack**

### 6.3 Configurar Stack

#### Name:
```
propzy
```

#### Build method:
⭐ **Repository** (NÃO use Web editor!)

#### Repository URL:
```
https://github.com/SEU-USUARIO/SEU-REPOSITORIO
```
Exemplo: `https://github.com/joaosilva/propzy`

#### Repository reference:
```
refs/heads/main
```
(ou `refs/heads/master` se usar master)

#### Compose path:
```
docker-compose.prod.yml
```

### 6.4 Git Credentials

**✅ Marcar:** Git credentials

- **Username:** `seu-usuario-github`
- **Personal Access Token:** `ghp_xxxxx...` (token que você copiou)

### 6.5 Automatic Updates

**✅ Marcar:** GitOps updates

- **Mechanism:** `Polling`
- **Polling interval:** `5m`
- **✅ Marcar:** Re-pull image and redeploy
- **✅ Marcar:** Force redeployment

### 6.6 Configurar Variáveis de Ambiente

**Scroll down:** Environment variables

**Click:** Advanced mode

**Cole este conteúdo:**

```bash
# Django
SECRET_KEY=GERE_UMA_CHAVE_AQUI
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings

# Domínio (AJUSTE SEU DOMÍNIO!)
BASE_DOMAIN=propzy.com.br
ALLOWED_HOSTS=.propzy.com.br,propzy.com.br
CSRF_TRUSTED_ORIGINS=https://.propzy.com.br,https://propzy.com.br

# Banco de Dados (CRIE SENHAS FORTES!)
DB_NAME=propzy_prod
DB_USER=propzy_user
DB_PASSWORD=Senha_Forte_Do_Banco_123!@#$
DB_HOST=db
DB_PORT=5432

# Redis (CRIE SENHA FORTE!)
REDIS_PASSWORD=Senha_Forte_Do_Redis_456!@#$
REDIS_HOST=redis
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://:Senha_Forte_Do_Redis_456!@#$@redis:6379/0
CELERY_RESULT_BACKEND=redis://:Senha_Forte_Do_Redis_456!@#$@redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@propzy.com.br

# Segurança
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**⚠️ GERAR SECRET_KEY:**

```bash
# No seu computador ou no servidor:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Cole o resultado em SECRET_KEY=
```

### 6.7 Deploy!

**Click:** **Deploy the stack**

**Aguarde 5-10 minutos:**
- Portainer clona repositório
- Faz build das imagens
- Sobe containers

**Acompanhe os logs na tela**

---

## ✅ PARTE 7: VERIFICAR CONTAINERS (2 min)

**Portainer:** Stacks → propzy

**Verificar se todos estão "running":**

- ✅ propzy-nginx (running)
- ✅ propzy-app (running)
- ✅ propzy-celery-worker (running)
- ✅ propzy-celery-beat (running)
- ✅ propzy-db (running)
- ✅ propzy-redis (running)
- ✅ propzy-certbot (running)
- ✅ propzy-watchtower (running)

**Se algum estiver com erro:**
- Click no container
- Ver **Logs**
- Corrigir problema

---

## 🗄️ PARTE 8: INICIALIZAR APLICAÇÃO (10 min)

### 8.1 Via Console do Portainer

**Containers** → **propzy-app** → **Console**

**Command:** `/bin/sh`

**Click:** Connect

### 8.2 Executar Comandos

```bash
# 1. Migrations
python manage.py migrate

# 2. Coletar estáticos
python manage.py collectstatic --noinput

# 3. Instalar temas
python manage.py install_themes

# 4. Criar superusuário
python manage.py createsuperuser
# Email: admin@propzy.com.br
# Senha: (senha forte!)
```

### 8.3 Verificar

```bash
# Listar temas instalados
python manage.py install_themes --scan

# Verificar banco
python manage.py check
```

---

## 🎨 PARTE 9: CRIAR LANDING PAGE DE TESTE (5 min)

### 9.1 Acessar Admin

```
https://propzy.com.br/admin/
```

**Login:**
- Email: admin@propzy.com.br
- Senha: (que você criou)

### 9.2 Criar Tema (se não tiver)

**Landings** → **Temas** → Verificar se tem "Modern Real Estate"

### 9.3 Criar Landing Page

**Landings** → **Landing Pages** → **Adicionar**

```
Proprietário: admin
Subdomínio: teste
Nome do Negócio: Imobiliária Teste
Descrição: As melhores casas e apartamentos
Email: contato@teste.com
Telefone: (11) 99999-9999
WhatsApp: 5511999999999
Tema: Modern Real Estate
Cor Primária: #2563eb
Cor Secundária: #7c3aed
✅ Publicada
✅ Ativa
```

**Salvar**

### 9.4 Criar Imóveis

**Landings** → **Imóveis** → **Adicionar**

```
Landing Page: Imobiliária Teste
Título: Casa 3 Quartos - Centro
Descrição: Linda casa no centro com 3 quartos, 2 banheiros
Tipo: Casa
Transação: Venda
Preço de Venda: 350000
Quartos: 3
Banheiros: 2
Vagas de Garagem: 2
Área (m²): 150
Endereço: Rua Exemplo, 123
Bairro: Centro
Cidade: Sua Cidade
Estado: SP
CEP: 01234-567
✅ Destaque
✅ Ativo
```

**Salvar**

**Adicione mais 2-3 imóveis variando os dados**

### 9.5 Testar Landing Page

```
https://teste.propzy.com.br
```

**Deve mostrar:**
- ✅ Nome "Imobiliária Teste"
- ✅ Imóveis cadastrados
- ✅ Botão WhatsApp
- ✅ Design profissional

🎉 **FUNCIONOU! Sistema no ar!**

---

## 🔐 PARTE 10: CONFIGURAR SSL AUTOMÁTICO (10 min)

### 10.1 Preparar Webroot

**Via SSH:**

```bash
# Criar diretório
mkdir -p /var/www/certbot
chmod -R 755 /var/www/certbot

# Verificar
ls -la /var/www/
```

### 10.2 Testar Geração de Certificado

**Via Console do Portainer** (propzy-app):

```bash
# Testar comando (não vai gerar ainda)
python manage.py manage_ssl --help

# Ver certificados atuais
python manage.py manage_ssl list
```

### 10.3 Configurar Renovação Automática

**Via SSH:**

```bash
# Adicionar ao crontab
crontab -e

# Adicionar linha (pressione 'i' para inserir):
0 3 * * * docker exec propzy-app python manage.py manage_ssl renew-all >> /var/log/ssl-renew.log 2>&1

# Salvar: ESC → :wq → Enter
```

**Pronto! SSL automático configurado! ✅**

---

## 🔔 PARTE 11: CONFIGURAR WEBHOOK (Opcional - 5 min)

### 11.1 Obter URL do Webhook

**Portainer:** Stacks → propzy → **Webhooks**

**Copiar URL:**
```
https://SEU_IP:9443/api/stacks/webhooks/abc123def456
```

### 11.2 Configurar no GitHub

**Seu repositório** → **Settings** → **Webhooks** → **Add webhook**

```
Payload URL: (cole URL do Portainer)
Content type: application/json
Secret: (deixe vazio)
Which events: Just the push event
✅ Active
```

**Add webhook**

### 11.3 Testar

```bash
# Fazer mudança qualquer
echo "# teste webhook" >> README.md
git add .
git commit -m "teste webhook"
git push

# Portainer deve detectar e fazer redeploy automático!
```

---

## ✅ VERIFICAÇÃO FINAL

### Checklist Completo:

```bash
# 1. DNS funcionando
nslookup propzy.com.br
nslookup teste.propzy.com.br
# Ambos retornam IPs do Cloudflare

# 2. SSL funcionando
curl -I https://propzy.com.br
# Retorna 200 OK

# 3. Subdomínio funcionando
curl -I https://teste.propzy.com.br
# Retorna 200 OK

# 4. Admin acessível
# https://propzy.com.br/admin/ (login OK)

# 5. Landing page funcionando
# https://teste.propzy.com.br (mostra imóveis)

# 6. Containers rodando
docker ps
# Todos "Up" e "healthy"

# 7. Auto-update funcionando
# Fazer push → Portainer detecta → Redeploy
```

---

## 🎯 SOBRE DOMÍNIOS PERSONALIZADOS DOS CLIENTES

### Como funciona para clientes:

**Cliente adiciona domínio personalizado no Admin:**
```
www.imobiliaria-cliente.com.br
```

**Cliente configura DNS (no registrador do domínio):**
```
Type: CNAME
Name: www
Target: propzy.com.br
```

**Sistema faz automaticamente:**
1. Detecta novo domínio (signal)
2. Aguarda 30s → Verifica DNS
3. Aguarda 2min → Gera certificado SSL (via webroot - porta 80)
4. Certificado instalado! ✅

**⚠️ IMPORTANTE:**
- Cliente NÃO precisa adicionar TXT manualmente!
- Sistema usa método **webroot** (não DNS)
- Funciona via porta 80 (HTTP challenge)
- **100% automático!**

---

## 🔄 WORKFLOW DE ATUALIZAÇÃO

### Quando você fizer mudanças no código:

```bash
# 1. Desenvolver localmente
git add .
git commit -m "Nova feature"
git push origin main

# 2. Portainer detecta automaticamente
# - Webhook (instantâneo)
# OU
# - Polling (a cada 5 minutos)

# 3. Portainer faz automaticamente:
# - git pull
# - rebuild das imagens alteradas
# - redeploy dos containers

# 4. Sistema atualizado em 2-5 min! 🚀
```

---

## 💰 CUSTOS

**Servidor VPS:**
- 2 CPU, 4GB RAM: ~$40-60/mês

**Outros:**
- Domínio: ~$10/ano
- Cloudflare: Grátis
- SSL: Grátis (Let's Encrypt)
- Portainer: Grátis (CE)

**Total:** ~$50/mês

---

## 📚 DOCUMENTAÇÃO

- **PORTAINER_GIT_DEPLOY.md** - Detalhes do deploy via Git
- **SSL_AUTOMATICO.md** - SSL para domínios personalizados
- **DEPLOY.md** - Deploy alternativo (SSH)

---

## 🆘 TROUBLESHOOTING

### Container não inicia

**Ver logs:**
```
Portainer → Containers → propzy-app → Logs
```

**Causas comuns:**
- .env com variáveis faltando
- Banco não iniciou ainda (aguardar)
- Erro no código Python

### Landing page retorna 404

**Verificar:**
- Landing page está **Publicada** e **Ativa**
- DNS aponta corretamente
- NGINX está rodando

### SSL não funciona

**Verificar:**
```bash
ls -la /etc/letsencrypt/live/propzy.com.br/
# Deve ter fullchain.pem e privkey.pem
```

**Regenerar se necessário:**
```bash
certbot renew --force-renewal
docker restart propzy-nginx
```

---

## ✅ RESUMO

**Você acabou de configurar:**

✅ VPS do zero
✅ Docker + Portainer
✅ DNS wildcard
✅ SSL wildcard
✅ Deploy via Git
✅ Auto-update (git push → deploy)
✅ Multi-tenant
✅ SSL automático para clientes
✅ Sistema completo em produção!

**Tempo total:** 60-90 minutos
**Resultado:** Sistema profissional funcionando! 🎉

---

**🎉 PARABÉNS! Sistema 100% operacional!**

**Próximos passos:**
1. Criar mais landing pages
2. Adicionar mais imóveis
3. Divulgar para clientes
4. Lucrar! 💰

**BOM USO! 🚀**

