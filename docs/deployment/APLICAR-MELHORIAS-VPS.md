# 🚀 Aplicar Melhorias na VPS

## ⚠️ IMPORTANTE - Leia antes de começar

Estas melhorias foram implementadas para aumentar a **segurança** e **escalabilidade** do sistema.

**Principais mudanças:**
- PostgreSQL não expõe mais porta 5432 (mais seguro)
- Redis agora requer senha
- SECRET_KEY obrigatória em produção
- Workers dinâmicos e autoscaling
- Logs persistentes

---

## 📋 Passo a Passo

### 1. Backup atual (OBRIGATÓRIO)

```bash
cd /root/apps/propzy
docker compose down
tar -czf backup-antes-melhorias-$(date +%Y%m%d).tar.gz infra/ backend/
```

### 2. Atualizar código do GitHub

```bash
cd /root/apps/propzy
git pull origin main
```

### 3. Atualizar arquivo .env

**IMPORTANTE:** Você DEVE adicionar estas novas variáveis:

```bash
cd infra
nano .env
```

**Adicione/atualize:**

```bash
# GERAR SECRET_KEY (se ainda não tiver uma forte)
SECRET_KEY=$(openssl rand -base64 50)

# ADICIONAR SENHA DO REDIS (escolha uma senha forte)
REDIS_PASSWORD=SUA_SENHA_FORTE_AQUI

# ATUALIZAR URLs do Redis (substitua SUA_SENHA_FORTE_AQUI)
CELERY_BROKER_URL=redis://:SUA_SENHA_FORTE_AQUI@redis:6379/0
CELERY_RESULT_BACKEND=redis://:SUA_SENHA_FORTE_AQUI@redis:6379/0
REDIS_URL=redis://:SUA_SENHA_FORTE_AQUI@redis:6379/1

# VALIDAR outras variáveis
DB_PASSWORD=senha_forte_postgres
ALLOWED_HOSTS=propzy.com.br,app.propzy.com.br,*.propzy.com.br
```

**Exemplo de .env completo:**

```bash
# Database
DB_NAME=propzy
DB_USER=postgres
DB_PASSWORD=senha_postgres_forte_123
DB_HOST=db
DB_PORT=5432

# Django
SECRET_KEY=gere_com_openssl_rand_base64_50
DEBUG=False
ALLOWED_HOSTS=propzy.com.br,app.propzy.com.br,*.propzy.com.br

# Redis (NOVO - OBRIGATÓRIO)
REDIS_PASSWORD=senha_redis_forte_456

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=noreply@propzy.com.br

# Redis / Celery (ATUALIZADO - com senha)
CELERY_BROKER_URL=redis://:senha_redis_forte_456@redis:6379/0
CELERY_RESULT_BACKEND=redis://:senha_redis_forte_456@redis:6379/0
REDIS_URL=redis://:senha_redis_forte_456@redis:6379/1

# Opcional
CREATE_SUPERUSER=false

# Domínios
VPS_IP=72.60.252.168
PROXY_DOMAIN=proxy.propzy.com.br
CERTBOT_EMAIL=seu-email@exemplo.com
```

### 4. Criar diretório de logs

```bash
cd /root/apps/propzy/infra
mkdir -p logs
chmod 755 logs
```

### 5. Recriar containers

```bash
cd /root/apps/propzy/infra
docker compose down
docker compose up -d --build
```

### 6. Verificar se está funcionando

```bash
# Ver status (todos devem estar "healthy")
docker compose ps

# Ver logs
docker compose logs --tail=50

# Verificar logs persistentes
ls -lh logs/
tail -f logs/django_errors.log

# Testar API
curl http://localhost/api/health/
```

### 7. Verificar segurança

```bash
# PostgreSQL NÃO deve mostrar porta 5432 exposta
docker compose ps db
# Deve mostrar apenas portas internas, não 0.0.0.0:5432

# Redis deve exigir senha
docker compose exec redis redis-cli ping
# Deve dar erro "NOAUTH Authentication required"

docker compose exec redis redis-cli -a SUA_SENHA_AQUI ping
# Deve retornar "PONG"
```

---

## ✅ Checklist de Verificação

- [ ] Backup criado antes de atualizar
- [ ] Código atualizado do GitHub
- [ ] `.env` atualizado com REDIS_PASSWORD
- [ ] URLs do Redis atualizadas com senha
- [ ] SECRET_KEY forte configurada
- [ ] Diretório `logs/` criado
- [ ] Containers recriados com sucesso
- [ ] Todos os serviços "healthy" (`docker compose ps`)
- [ ] PostgreSQL não expõe porta 5432
- [ ] Redis exige autenticação
- [ ] Logs sendo gerados em `infra/logs/`
- [ ] API `/api/health/` funcionando
- [ ] Site acessível via HTTPS

---

## 🚨 Troubleshooting

### Erro: "SECRET_KEY environment variable is required"

**Solução:** Adicione SECRET_KEY no .env
```bash
SECRET_KEY=$(openssl rand -base64 50)
```

### Erro: Redis "NOAUTH Authentication required"

**Solução:** Atualize as URLs do Redis no .env com a senha:
```bash
CELERY_BROKER_URL=redis://:SUA_SENHA@redis:6379/0
```

### Erro: Container "unhealthy"

**Solução:** Ver logs do container:
```bash
docker compose logs nome_do_container --tail=100
```

### Erro 502 Bad Gateway

**Solução:** Recarregar Nginx:
```bash
docker compose exec nginx nginx -s reload
```

### Containers não iniciam

**Solução:** Ver logs:
```bash
docker compose logs --tail=100
```

---

## 📊 Monitoramento Contínuo

Após aplicar, monitore:

```bash
# Ver logs em tempo real
docker compose logs -f

# Ver apenas erros
tail -f /root/apps/propzy/infra/logs/django_errors.log

# Ver logs de segurança
tail -f /root/apps/propzy/infra/logs/security.log

# Status dos containers
watch -n 5 'docker compose ps'
```

---

## 🔄 Rollback (se necessário)

Se algo der errado:

```bash
cd /root/apps/propzy
docker compose down
tar -xzf backup-antes-melhorias-YYYYMMDD.tar.gz
cd infra
docker compose up -d
```

---

## 📞 Suporte

Se encontrar problemas, verifique:
1. Logs do container: `docker compose logs nome_container`
2. Logs da aplicação: `tail -f logs/django_errors.log`
3. Configuração do .env
4. Status dos containers: `docker compose ps`

---

**Tempo estimado:** 10-15 minutos
**Downtime:** ~2 minutos (durante recriação dos containers)

