# 🏗️ Infraestrutura

Estrutura organizada da infraestrutura do projeto Propzy com segurança e boas práticas.

## 📂 Estrutura de Pastas

```
infra/
├── development/          # 🛠️ DESENVOLVIMENTO LOCAL
│   ├── docker-compose.yml    # Web + DB + Redis + Celery Worker + Celery Beat
│   ├── start_celery_worker.sh # Script usado pelo container celery_worker
│   ├── start_celery_beat.sh  # Script usado pelo container celery_beat
│   └── README.md
│
├── production/           # 🚀 PRODUÇÃO/SERVIDOR
│   ├── docker-compose.yml    # Web + DB + Redis + Celery Worker + Celery Beat
│   ├── start_celery_worker.sh # Script usado pelo container celery_worker
│   ├── start_celery_beat.sh  # Script usado pelo container celery_beat
│   └── README.md
│
└── scripts/              # 📜 SCRIPTS COMPARTILHADOS
    ├── entrypoint.sh     # Usado pelo container web (migrations, collectstatic, etc)
    └── README.md
```

## 🎯 Quando Usar Cada Pasta

### `development/` - Desenvolvimento Local
- ✅ Use quando estiver desenvolvendo localmente
- ✅ Docker Compose com containers separados (web, db, redis, celery_worker, celery_beat)
- ✅ Cada serviço em seu próprio container (boa prática)
- ✅ Volumes montados para desenvolvimento rápido
- ❌ **NÃO** usar em produção

### `production/` - Produção/Servidor
- ✅ Use para configurações do servidor real
- ✅ Docker Compose idêntico ao desenvolvimento (mas com settings de produção)
- ✅ Cada serviço em seu próprio container (boa prática)
- ✅ Configurações otimizadas para produção
- ❌ **NÃO** usar localmente

### `scripts/` - Compartilhados
- ✅ Scripts usados em ambos os ambientes
- ✅ Entrypoint do Docker
- ⚠️ Modificar com cuidado

## 🚀 Quick Start

### Desenvolvimento
```bash
# Na raiz do projeto (usa docker-compose.yml da raiz)
docker-compose up -d

# Verificar status
docker-compose ps

# Você verá 5 containers: web, db, redis, celery_worker, celery_beat
```

### Produção
```bash
# Na pasta infra/production
cd infra/production
docker-compose up -d

# IMPORTANTE: Configure .env primeiro!
```

## 🔐 Segurança

### Desenvolvimento
- ✅ Portas expostas para debug (8000, 5432, 6379)
- ✅ Senhas simples permitidas
- ✅ Volumes montados para hot-reload

### Produção
- 🔒 DB e Redis **SEM portas expostas**
- 🔒 Apenas web exposta (para Nginx/proxy)
- 🔒 Senhas fortes obrigatórias
- 🔒 Volumes read-only onde possível
- 🔒 Limites de recursos configurados

## 📝 Notas

- **Desenvolvimento**: Tudo em `infra/development/` é apenas para local
- **Produção**: Configurações em `infra/production/` são para o servidor
- **Compartilhados**: Scripts em `infra/scripts/` são usados em ambos



