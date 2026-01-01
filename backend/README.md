# 🏢 Propzy - Plataforma Multi-Tenant SaaS

Sistema multi-tenant completo para gerenciamento de imobiliárias com domínios personalizados e certificados SSL automáticos.

## 📋 Índice

- [Arquitetura](#arquitetura)
- [Quick Start - Desenvolvimento](#quick-start---desenvolvimento)
- [Quick Start - Produção](#quick-start---produção)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Segurança](#segurança)
- [Celery](#celery)

## 🏗️ Arquitetura

### Serviços

- **Web** - Django com Gunicorn
- **PostgreSQL** - Banco de dados
- **Redis** - Cache e broker do Celery
- **Celery Worker** - Processamento assíncrono
- **Celery Beat** - Agendamento de tarefas

### Ambientes

- **Desenvolvimento** - Portas expostas para debug, volumes montados
- **Produção** - Segurança máxima, sem portas expostas (DB/Redis), volumes read-only

## 🚀 Quick Start - Desenvolvimento

### 1. Clonar e Configurar

```bash
# Clonar repositório
git clone <repo-url>
cd propzy

# Criar arquivo .env
cp .env.example .env

# Editar .env conforme necessário
nano .env
```

### 2. Iniciar com Docker Compose

```bash
# Subir todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f
```

Você verá **5 containers**:
- `propzy_dev_web` - Web Django (http://localhost:8000)
- `propzy_dev_db` - PostgreSQL (porta 5432)
- `propzy_dev_redis` - Redis (porta 6379)
- `propzy_dev_celery_worker` - Worker
- `propzy_dev_celery_beat` - Beat

### 3. Acessar

- **Web**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🔒 Quick Start - Produção

### 1. Configurar Variáveis de Ambiente

```bash
# Copiar template de produção
cp .env.production.example .env

# IMPORTANTE: Gerar SECRET_KEY forte
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Editar .env com valores de produção
nano .env
```

### 2. Deploy

```bash
cd infra/production

# Carregar variáveis de ambiente
set -a; source ../../.env; set +a

# Subir serviços
docker-compose up -d

# Verificar status
docker-compose ps
```

### Diferenças de Produção

✅ **Seguro**:
- DB e Redis **SEM portas expostas** (apenas rede interna)
- Web exposta apenas para Nginx/proxy reverso
- Volumes read-only para static files
- Limites de recursos (CPU/RAM)
- Healthchecks em todos os serviços

## 📁 Estrutura do Projeto

```
propzy/
├── apps/                      # Apps Django
│   ├── billing/               # Cobrança e planos
│   ├── common/                # Utilidades compartilhadas
│   ├── dashboard/             # Dashboard
│   ├── domains/               # Gerenciamento de domínios
│   ├── public_site/           # Site público
│   ├── tenants/               # Multi-tenancy
│   └── users/                 # Autenticação e usuários
│
├── config/                    # Configurações Django
│   ├── settings/              
│   │   ├── base.py            # Configurações base
│   │   ├── local.py           # Desenvolvimento
│   │   └── production.py      # Produção
│   ├── celery.py              # Configuração Celery
│   ├── urls.py                # URLs principais
│   └── wsgi.py                # WSGI
│
├── infra/                     # Infraestrutura
│   ├── development/           # Scripts de desenvolvimento
│   │   ├── start_celery_worker.sh
│   │   ├── start_celery_beat.sh
│   │   └── README.md
│   │
│   ├── production/            # Configuração de produção
│   │   ├── docker-compose.yml  # ⚠️ PRODUÇÃO
│   │   ├── start_celery_worker.sh
│   │   ├── start_celery_beat.sh
│   │   └── README.md
│   │
│   └── scripts/               # Scripts compartilhados
│       ├── entrypoint.sh      # Inicialização containers
│       └── README.md
│
├── templates/                 # Templates Django
├── static/                    # Arquivos estáticos
├── docker-compose.yml         # ⚠️ DESENVOLVIMENTO (devcontainer)
├── Dockerfile                 # Imagem Docker
├── .env.example               # Template variáveis (dev)
├── .env.production.example    # Template variáveis (prod)
├── requirements.txt           # Dependências Python
└── manage.py                  # Django CLI

```

## 🔐 Segurança

### Desenvolvimento

- ✅ Portas expostas para debug (8000, 5432, 6379)
- ✅ Senhas simples no `.env.example`
- ✅ DEBUG=True permitido
- ✅ Volumes montados para hot-reload

### Produção

- 🔒 **DB e Redis SEM portas expostas** (apenas rede interna)
- 🔒 **SECRET_KEY forte obrigatória**
- 🔒 **DEBUG=False sempre**
- 🔒 **Senhas fortes obrigatórias**
- 🔒 **HTTPS/SSL obrigatório**
- 🔒 **Volumes read-only** onde possível
- 🔒 **Limites de recursos** configurados
- 🔒 **Healthchecks** em todos os serviços

### Boas Práticas

1. **NUNCA commite** `.env`
2. **Gere SECRET_KEY única** para cada ambiente
3. **Use senhas fortes** em produção
4. **Habilite HTTPS** sempre
5. **Monitore logs** regularmente
6. **Faça backups** do banco de dados

## 📊 Celery

### Tarefas Configuradas

- `verify_all_pending_domains` - Verifica domínios pendentes (a cada 30 min)
- `verify_domain` - Verifica domínio específico
- `generate_ssl_certificate` - Gera certificado SSL
- `renew_certificates` - Renova certificados

### Comandos Úteis

```bash
# Ver workers ativos
celery -A config.celery inspect active

# Ver tarefas agendadas
celery -A config.celery inspect scheduled

# Ver estatísticas
celery -A config.celery inspect stats

# Ver logs do worker
docker-compose logs -f celery_worker

# Ver logs do beat
docker-compose logs -f celery_beat
```

## 🛠️ Comandos Úteis

### Desenvolvimento

```bash
# Iniciar tudo
docker-compose up -d

# Parar tudo
docker-compose down

# Ver logs
docker-compose logs -f [service_name]

# Rebuild containers
docker-compose up -d --build

# Executar comando no container
docker-compose exec web python manage.py shell

# Criar migrações
docker-compose exec web python manage.py makemigrations

# Aplicar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Coletar static files
docker-compose exec web python manage.py collectstatic
```

### Produção

```bash
# Deploy/Atualizar
cd infra/production
docker-compose up -d --build

# Ver status
docker-compose ps

# Backup do banco
docker-compose exec db pg_dump -U ${DB_USER} ${DB_NAME} > backup.sql

# Restaurar banco
docker-compose exec -T db psql -U ${DB_USER} ${DB_NAME} < backup.sql
```

## 📖 Documentação Adicional

- [Infraestrutura](infra/README.md)
- [Celery](README_CELERY.md)
- [Desenvolvimento](infra/development/README.md)
- [Produção](infra/production/README.md)

## 🤝 Contribuindo

1. Siga as boas práticas de segurança
2. Teste em desenvolvimento antes de produção
3. Documente mudanças significativas
4. Mantenha os READMEs atualizados

## 📝 Licença

[Sua licença aqui]























