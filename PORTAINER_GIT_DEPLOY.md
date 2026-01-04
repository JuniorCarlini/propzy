# 🚀 Deploy via Portainer com Git Repository

## ✨ Deploy Automático com Auto-Update

Este guia mostra como fazer deploy do sistema usando **Git Repository** no Portainer, com **atualização automática** quando você fizer `git push`.

---

## 📋 PRÉ-REQUISITOS

- [x] VPS com Portainer instalado
- [x] Código no GitHub/GitLab
- [x] DNS configurado (wildcard)
- [x] SSL gerado no servidor (`/etc/letsencrypt/`)

---

## 🔑 PASSO 1: Criar Token do GitHub (5 min)

### No GitHub:

1. **Acesse:** https://github.com/settings/tokens
2. **Generate new token** → **Tokens (classic)**
3. **Note:** `Portainer Propzy Deploy`
4. **Expiration:** 90 days (ou No expiration)
5. **Selecione permissões:**
   - ✅ **repo** (Full control of private repositories)
6. **Generate token**
7. **COPIE O TOKEN** ⚠️ (só aparece uma vez!)

```
Exemplo: ghp_1234567890abcdefghijklmnopqrstuvwxyzABCD
```

**⚠️ IMPORTANTE:** Guarde esse token em local seguro!

---

## 🐳 PASSO 2: Criar Stack no Portainer (10 min)

### 2.1 Acessar Portainer

```
https://72.60.252.168:9443
```

### 2.2 Ir para Stacks

**Menu lateral:** Stacks → **Add stack**

### 2.3 Configurar Stack

#### **Name:**
```
propzy
```

#### **Build method:**
⭐ **Repository** (NÃO use Web editor!)

#### **Repository URL:**
```
https://github.com/SEU-USUARIO/SEU-REPOSITORIO
```

Exemplo: `https://github.com/joaosilva/propzy`

#### **Repository reference:**
```
refs/heads/main
```

Se usar branch `master`:
```
refs/heads/master
```

#### **Compose path:**
```
docker-compose.prod.yml
```

### 2.4 Authentication

**✅ Marcar:** Git credentials

- **Username:** `seu-usuario-github`
- **Personal Access Token:** `ghp_...` (token que você copiou)

### 2.5 Automatic Updates

**✅ Marcar:** GitOps updates

**Mechanism:** `Polling` ou `Webhook`

**Se escolher Polling:**
- **Polling interval:** `5m` (5 minutos)

**Se escolher Webhook:**
- Portainer vai gerar URL
- Você configura no GitHub (passo 3)

**✅ Marcar:** Re-pull image and redeploy

**✅ Marcar:** Force redeployment

---

## 📝 PASSO 3: Configurar Variáveis de Ambiente

**Scroll down:** Environment variables

### Opção A: Load from .env file (Recomendado)

**Click:** Advanced mode

**Cole o conteúdo:**

```bash
# Django
SECRET_KEY=GERE_UMA_CHAVE_FORTE_AQUI
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings

# Domínio
BASE_DOMAIN=propzy.com.br
ALLOWED_HOSTS=.propzy.com.br,propzy.com.br
CSRF_TRUSTED_ORIGINS=https://.propzy.com.br,https://propzy.com.br

# Banco de Dados (CRIE SENHAS FORTES!)
DB_NAME=propzy_prod
DB_USER=propzy_user
DB_PASSWORD=SuaSenhaForteDoBanco123!@#
DB_HOST=db
DB_PORT=5432

# Redis (CRIE SENHA FORTE!)
REDIS_PASSWORD=SuaSenhaForteDoRedis456!@#
REDIS_HOST=redis
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://:SuaSenhaForteDoRedis456!@#@redis:6379/0
CELERY_RESULT_BACKEND=redis://:SuaSenhaForteDoRedis456!@#@redis:6379/0

# Email (configure depois se quiser)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@propzy.com.br

# Segurança
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**⚠️ IMPORTANTE:** Gere SECRET_KEY forte:

```bash
# No seu computador:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Cole o resultado em SECRET_KEY
```

### Opção B: Adicionar variável por variável

Se preferir, pode adicionar uma por uma clicando em **+ add environment variable**

---

## 🚀 PASSO 4: Deploy!

**Click:** **Deploy the stack**

### O que vai acontecer:

```
1. Portainer clona repositório do GitHub
   ↓
2. Lê docker-compose.prod.yml
   ↓
3. Faz build das imagens (Django app)
   ↓
4. Sobe todos os containers
   ↓
5. Aguarde 3-5 minutos ⏳
   ↓
6. Stack rodando! ✅
```

**Logs em tempo real:**
- Você verá o progresso na tela
- Se der erro, mostra mensagem

---

## ✅ PASSO 5: Inicializar Aplicação (5 min)

Depois que todos containers subirem:

### Via Portainer Console:

1. **Containers** → **propzy-app** → **Console**
2. **Connect**
3. Executar comandos:

```bash
# Migrations
python manage.py migrate

# Coletar estáticos
python manage.py collectstatic --noinput

# Instalar temas
python manage.py install_themes

# Criar superusuário
python manage.py createsuperuser
# Email: admin@propzy.com.br
# Senha: (senha forte)
```

### Via SSH (alternativa):

```bash
docker exec propzy-app python manage.py migrate
docker exec propzy-app python manage.py collectstatic --noinput
docker exec propzy-app python manage.py install_themes
docker exec -it propzy-app python manage.py createsuperuser
```

---

## 🔔 PASSO 6: Configurar Webhook (Opcional - Auto-update instantâneo)

Se escolheu Webhook no passo 2:

### No Portainer:

1. **Stacks** → **propzy** → **Webhooks**
2. Copie a URL gerada

Exemplo:
```
https://72.60.252.168:9443/api/stacks/webhooks/abc123def456
```

### No GitHub:

1. **Seu repositório** → **Settings** → **Webhooks**
2. **Add webhook**
3. **Payload URL:** (cole URL do Portainer)
4. **Content type:** `application/json`
5. **Secret:** (deixe vazio)
6. **Which events:** Just the push event
7. **Active:** ✅
8. **Add webhook**

### Testar:

```bash
# Fazer uma mudança qualquer
echo "# teste" >> README.md
git add .
git commit -m "teste webhook"
git push

# Webhook notifica Portainer
# Portainer faz pull e redeploy automático!
```

---

## 🎯 AUTO-UPDATE FUNCIONANDO

### Como funciona:

**Quando você faz `git push`:**

```
1. GitHub recebe push
   ↓
2. GitHub notifica Portainer (webhook)
   ↓
3. Portainer faz git pull
   ↓
4. Portainer reconstrói imagens alteradas
   ↓
5. Portainer faz redeploy dos containers
   ↓
6. Aplicação atualizada! ✅
```

**Tempo:** 2-5 minutos (automático)

---

## 📊 MONITORAMENTO

### Ver Status no Portainer:

**Stacks → propzy:**
- **Containers:** Todos "running" ✅
- **Last update:** Timestamp da última atualização
- **Git commit:** SHA do commit atual

### Ver Logs:

**Containers → propzy-app → Logs:**
- Auto-refresh: ✅
- Lines: 100

### Ver Código:

**Containers → propzy-app → Console:**
```bash
ls -la /app/
cat /app/manage.py
git log -5
```

---

## 🔄 ATUALIZAR MANUALMENTE

Se precisar forçar atualização:

**Portainer → Stacks → propzy:**
1. **Update the stack**
2. **✅ Pull latest image version**
3. **Update**

Ou via Git webhook:

**Stacks → propzy → Webhooks → Trigger**

---

## 🛠️ TROUBLESHOOTING

### 1. Erro ao clonar repositório

**Erro:** `Authentication failed`

**Solução:**
- Verifique se token está correto
- Verifique se token tem permissão `repo`
- Token expirou? Crie novo

### 2. Build falha

**Erro:** `Cannot build image`

**Solução:**
```bash
# Verificar se Dockerfile.prod existe
# Verificar se tem erros no Dockerfile
# Ver logs completos no Portainer
```

### 3. Container não inicia

**Erro:** Container fica reiniciando

**Solução:**
```bash
# Ver logs do container
Containers → propzy-app → Logs

# Geralmente é:
# - .env.prod com variáveis faltando
# - Banco não iniciou ainda (aguardar)
# - Erro de código Python
```

### 4. Webhook não funciona

**Erro:** Push não atualiza automaticamente

**Solução:**
- Verificar se webhook está ativo no GitHub
- Verificar URL do webhook
- Ver deliveries no GitHub Webhooks
- Usar Polling como alternativa

### 5. Código não atualiza

**Erro:** Fiz push mas código não mudou

**Solução:**
```bash
# Verificar branch correto no Portainer
# Limpar cache:
Stacks → propzy → Update → Force redeployment
```

---

## 💡 DICAS

### 1. Desenvolvimento:

```bash
# Branch de dev
git checkout -b develop
git push origin develop

# No Portainer:
# Criar stack "propzy-dev"
# Repository reference: refs/heads/develop
```

### 2. Rollback:

```bash
# Ver commits anteriores
git log --oneline

# Voltar para commit anterior
git reset --hard COMMIT_SHA
git push -f origin main

# Portainer faz pull e redeploy automático
```

### 3. Variáveis de Ambiente:

```bash
# Alterar variáveis:
Stacks → propzy → Editor → Environment variables

# Redeploy após mudança
```

### 4. Visualizar Código:

```bash
# Console do container
Containers → propzy-app → Console

# Comandos úteis:
ls -la /app/
cat /app/config/settings.py
python manage.py shell
```

---

## ✅ CHECKLIST COMPLETO

### Setup Inicial:
- [ ] Token GitHub criado
- [ ] Stack criada no Portainer
- [ ] Git credentials configurados
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy executado com sucesso
- [ ] Migrations executadas
- [ ] Superusuário criado
- [ ] Sistema acessível

### Auto-Update:
- [ ] Webhook configurado (GitHub)
- [ ] Webhook testado (push)
- [ ] OU Polling ativado (5 min)
- [ ] Auto-update funcionando

### Produção:
- [ ] SSL funcionando
- [ ] Subdomínios funcionando
- [ ] Landing pages criadas
- [ ] Backup configurado
- [ ] Monitoramento ativo

---

## 🎉 PRONTO!

**Seu sistema está rodando com:**

✅ Deploy automático via Git
✅ Auto-update quando fizer push
✅ Gerenciamento visual no Portainer
✅ Rollback fácil
✅ Logs em tempo real
✅ Console integrado

**Workflow:**

```bash
# Desenvolver localmente
git add .
git commit -m "Nova feature"
git push

# Portainer detecta (webhook ou polling)
# Atualiza automaticamente
# Sistema atualizado em 2-5 min! 🚀
```

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- **DEPLOY.md** - Deploy manual (SSH)
- **SSL_AUTOMATICO.md** - SSL para domínios personalizados
- **PORTAINER_STACK.txt** - Stack alternativa (copiar/colar)

---

**Tempo Total:** 30-45 minutos
**Dificuldade:** ⭐⭐ (Fácil)
**Resultado:** Sistema em produção com auto-update! 🎯

**BOA SORTE! 🚀**

