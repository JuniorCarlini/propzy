# 🚀 Produção/Servidor

Esta pasta contém configurações e scripts para **produção/servidor** com segurança máxima.

## 📁 Estrutura

- `docker-compose.yml` - Configuração Docker Compose completa para produção
- `start_celery_worker.sh` - Script usado pelo container do Celery Worker
- `start_celery_beat.sh` - Script usado pelo container do Celery Beat

## 🚀 Como Usar

### 1. Configurar Variáveis de Ambiente

```bash
# Na raiz do projeto, criar .env
cp .env.production.example .env

# IMPORTANTE: Gerar SECRET_KEY forte
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Editar .env com valores reais
nano .env
```

### 2. Deploy em Produção

```bash
# Ir para pasta de produção
cd infra/production

# Carregar variáveis de ambiente
set -a; source ../../.env; set +a

# Subir todos os serviços
docker-compose up -d --build

# Verificar status
docker-compose ps
```

Isso iniciará **todos os serviços em containers separados**:
- `web` - Aplicação Django (Gunicorn com 4 workers)
- `db` - PostgreSQL
- `redis` - Redis (broker do Celery)
- `celery_worker` - Celery Worker (container separado)
- `celery_beat` - Celery Beat (container separado)

### Verificar Status

```bash
# Ver todos os containers
docker-compose -f infra/production/docker-compose.yml ps

# Ver logs
docker-compose -f infra/production/docker-compose.yml logs -f
```

## 🔒 Segurança (Produção)

### ✅ Implementado

- 🔒 **DB e Redis SEM portas expostas** (apenas rede interna)
- 🔒 **Apenas web exposta** (porta 8000 para Nginx/proxy)
- 🔒 **Volumes read-only** para static files
- 🔒 **Limites de recursos** (CPU/RAM) configurados
- 🔒 **Healthchecks** em todos os serviços
- 🔒 **Redes internas** isoladas
- 🔒 **Senhas obrigatórias** para Redis

### ⚠️ Checklist de Segurança

Antes de fazer deploy, verifique:

- [ ] SECRET_KEY única e forte configurada
- [ ] DB_PASSWORD forte configurado
- [ ] REDIS_PASSWORD forte configurado
- [ ] DEBUG=False no .env
- [ ] ALLOWED_HOSTS configurado corretamente
- [ ] HTTPS/SSL configurado no Nginx
- [ ] Backups automáticos configurados
- [ ] Monitoramento de logs ativo

## 🛠️ Manutenção

### Backup do Banco de Dados

```bash
# Criar backup
docker-compose exec db pg_dump -U ${DB_USER} ${DB_NAME} > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T db psql -U ${DB_USER} ${DB_NAME} < backup_20240101.sql
```

### Atualizar Aplicação

```bash
# Pull do código
git pull origin main

# Rebuild e restart
docker-compose up -d --build

# Verificar logs
docker-compose logs -f
```

### Ver Logs

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f web
docker-compose logs -f celery_worker
```

## 📊 Monitoramento

### Ver Status dos Serviços

```bash
# Status dos containers
docker-compose ps

# Recursos utilizados
docker stats

# Celery workers ativos
docker-compose exec web celery -A config.celery inspect active
```

## ⚠️ Importante

- **NUNCA** use configurações de desenvolvimento em produção
- **SEMPRE** use senhas fortes
- **SEMPRE** use HTTPS
- **Faça backups** regularmente
- **Monitore logs** constantemente
- **Teste deploys** em staging primeiro



