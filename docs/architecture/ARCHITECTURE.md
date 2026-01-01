# Arquitetura SaaS Multi-Domínio com Django (Best Practices)

## Visão Geral

Este documento descreve a arquitetura completa de um SaaS escalável focado em imobiliárias e corretores de imóveis, utilizando Django como backend principal, Bootstrap no frontend, infraestrutura containerizada com Docker e suporte total a subdomínios e domínios personalizados, sem qualquer configuração manual no servidor.

O sistema é multi-tenant baseado em domínio, seguro por design, preparado para internacionalização e escalável desde o primeiro cliente.

---

## Stack Tecnológica

### Backend
- **Python 3.12**
- **Django 5.x**
- **Django Rest Framework**
- **PostgreSQL**
- **Redis**
- **Celery + Celery Beat**

### Frontend
- **Bootstrap 5.3+**
- **Django Templates**
- **HTMX** (opcional, recomendado)

### Infraestrutura
- **Docker**
- **Docker Compose**
- **Nginx**
- **Gunicorn**
- **Cloudflare** (DNS, SSL, WAF)
- **Hostinger VPS** (Ubuntu 22.04+)
- **Storage S3-compatible** (MinIO ou similar)

---

## Conceito Central: Multi-Tenant por Domínio

Cada cliente (tenant) é identificado exclusivamente pelo domínio ou subdomínio utilizado na requisição HTTP.

> **Um domínio = um tenant**

Não existem múltiplas instâncias do Django. Existe **uma aplicação**, que se adapta dinamicamente conforme o domínio acessado.

---

## Estrutura de URLs

### Público
- `propzy.com.br` → Landing page do SaaS
- `cliente.propzy.com.br` → Site público do cliente
- `cliente.com.br` → Site público do cliente (domínio próprio)

### Administrativo
- `app.propzy.com.br` → Dashboard SaaS e dashboard dos clientes

**⚠️ Regra importante:** Nunca misturar área pública com painel administrativo no mesmo domínio.

---

## Estrutura do Projeto Django

```
backend/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── production.py
│   │   └── local.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── tenants/
│   ├── domains/
│   ├── users/
│   ├── public_site/
│   ├── dashboard/
│   ├── billing/
│   └── common/
└── locale/
```

Cada app possui **responsabilidade única**, seguindo SRP (Single Responsibility Principle).

---

## Modelagem de Dados Essencial

### Tenant

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Identificador único |
| `name` | String | Nome do cliente |
| `slug` | String | Slug único para URLs |
| `plan` | Enum | Plano de assinatura |
| `is_active` | Boolean | Status ativo/inativo |
| `created_at` | DateTime | Data de criação |

### Domain

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Identificador único |
| `tenant` | FK → Tenant | Cliente proprietário |
| `domain` | String | Domínio completo |
| `type` | Enum | SUBDOMAIN \| CUSTOM |
| `is_verified` | Boolean | Domínio verificado |
| `created_at` | DateTime | Data de criação |

### User

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Identificador único |
| `tenant` | FK → Tenant | Cliente vinculado |
| `email` | String | Email único por tenant (usado como login) |
| `password` | String | Hash bcrypt |
| `is_active` | Boolean | Status ativo/inativo |

**⚠️ Importante:** 
- O sistema utiliza **email como login** (não username)
- Permissões são gerenciadas via **Grupos do Django** (não campo `role`)
- Cada usuário pode pertencer a múltiplos grupos dentro do tenant

---

## Middleware de Tenant (Ponto Crítico)

Um middleware é responsável por:

1. Ler o `Host` da requisição HTTP
2. Buscar o domínio na tabela `Domain`
3. Associar o tenant à `request`
4. Bloquear domínios não verificados

**Resultado:** `request.tenant` disponível em toda a aplicação.

**⚠️ Regra crítica:** Toda query do sistema deve ser filtrada pelo tenant para garantir isolamento total de dados.

---

## Autenticação e Permissões

### Autenticação por Email

O sistema utiliza **email como campo de login** ao invés de username tradicional.

**Configuração Django:**

```python
# settings/base.py
AUTH_USER_MODEL = 'users.User'

# Customizar backend de autenticação
AUTHENTICATION_BACKENDS = [
    'apps.users.backends.EmailBackend',  # Backend customizado
    'django.contrib.auth.backends.ModelBackend',
]
```

**Model User Customizado:**

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    email = models.EmailField(unique=False)  # Único apenas por tenant
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remover username dos campos obrigatórios
    
    class Meta:
        unique_together = [['tenant', 'email']]  # Email único por tenant
```

**Backend de Autenticação Customizado:**

```python
# apps/users/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email', username)
        tenant = getattr(request, 'tenant', None)
        
        if not email or not password or not tenant:
            return None
        
        try:
            user = User.objects.get(email=email, tenant=tenant, is_active=True)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
```

### Sistema de Permissões com Grupos Django

O sistema utiliza **Grupos padrão do Django** para gerenciar permissões e acessos dentro do site.

**Vantagens:**

- ✅ Sistema nativo e robusto do Django
- ✅ Permissões granulares por modelo/ação
- ✅ Múltiplos grupos por usuário
- ✅ Fácil gerenciamento via admin ou código
- ✅ Integração perfeita com decorators e mixins

**Grupos Padrão Sugeridos:**

| Grupo | Descrição | Permissões |
|-------|-----------|------------|
| `Tenant Admin` | Administrador do tenant | Todas as permissões do tenant |
| `Manager` | Gerente | Criar, editar, visualizar (sem deletar) |
| `Editor` | Editor de conteúdo | Criar e editar conteúdo público |
| `Viewer` | Visualizador | Apenas leitura |
| `Agent` | Corretor | Gerenciar próprios imóveis e leads |

**Criação de Grupos (via Management Command):**

```python
# apps/users/management/commands/create_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Criar grupos padrão
        groups = {
            'Tenant Admin': ['add', 'change', 'delete', 'view'],
            'Manager': ['add', 'change', 'view'],
            'Editor': ['add', 'change', 'view'],
            'Viewer': ['view'],
            'Agent': ['add', 'change', 'view'],  # Com filtro por usuário
        }
        
        for group_name, permissions in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            # Adicionar permissões específicas conforme necessário
```

**Uso em Views:**

```python
# apps/dashboard/views.py
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin

# Via decorator
@login_required
@permission_required('app.add_property', raise_exception=True)
def create_property(request):
    # View protegida por permissão
    pass

# Via class-based view
class PropertyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'app.add_property'
    # ...
```

**Verificação de Grupo:**

```python
# Verificar se usuário pertence a grupo específico
if request.user.groups.filter(name='Tenant Admin').exists():
    # Acesso de administrador
    pass

# Verificar múltiplos grupos
if request.user.groups.filter(name__in=['Tenant Admin', 'Manager']).exists():
    # Acesso de admin ou manager
    pass
```

**Isolamento por Tenant:**

**⚠️ Regra crítica:** Grupos e permissões devem sempre considerar o contexto do tenant. Um usuário pode ter diferentes grupos em diferentes tenants.

```python
# Filtrar permissões por tenant
def get_user_permissions(user, tenant):
    # Retornar apenas permissões válidas para o tenant atual
    return user.user_permissions.filter(
        # Aplicar lógica de filtro por tenant
    )
```

---

## Infraestrutura com Docker

### Estrutura de Infra

```
infra/
├── docker-compose.yml
├── nginx/
│   ├── nginx.conf
│   └── sites-enabled/
├── scripts/
│   ├── deploy-production.sh
│   ├── entrypoint.sh
│   ├── setup-completo.sh
│   ├── copy-certificates.sh
│   ├── generate-certificate.sh
│   └── renew-certificates.sh
└── .env.example
```

### Serviços no Docker Compose

| Serviço | Descrição |
|---------|-----------|
| `web` | Django + Gunicorn |
| `db` | PostgreSQL |
| `redis` | Cache e broker Celery |
| `celery` | Worker assíncrono |
| `celery-beat` | Agendador de tarefas |
| `nginx` | Proxy reverso |

### Deploy

```bash
docker compose up -d --build
```

Ou via script automatizado:

```bash
./scripts/deploy-production.sh
```

Ou deploy automático via GitHub Actions (ver `.github/workflows/deploy.yml`).

O deploy executa automaticamente:

- ✅ Migrações do banco de dados
- ✅ Coleta de arquivos estáticos
- ✅ Restart controlado dos serviços
- ✅ Limpeza de cache

---

## Subdomínios (Wildcard)

### Configuração no Cloudflare

```
Tipo: A
Nome: *
Conteúdo: IP do VPS
Proxy: Ativado (Laranja)
```

Com SSL Wildcard ativo.

**✅ Resultado:** Nenhuma configuração adicional no servidor é necessária. Qualquer subdomínio `*.propzy.com.br` funciona automaticamente.

---

## Domínios Personalizados dos Clientes

### Fluxo do Cliente

1. Cliente cadastra domínio no painel administrativo
2. Sistema gera instruções DNS personalizadas
3. Cliente copia e cola no provedor DNS dele
4. Sistema valida automaticamente via Celery
5. Domínio é liberado quando verificado

### Exemplo de Configuração DNS

```
Tipo: CNAME
Host: @
Destino: proxy.propzy.com.br
TTL: Auto
```

Ou via registro A:

```
Tipo: A
Host: @
Destino: IP do VPS
TTL: Auto
```

---

## Verificação Automática de Domínio

Realizada via **Celery Task** periódica:

1. Resolve DNS do domínio
2. Verifica IP ou CNAME apontando corretamente
3. Confirma chegada da requisição HTTP
4. Marca domínio como `is_verified = True`

**✅ Resultado:** Nenhuma ação manual envolvida. Processo 100% automatizado.

---

## SSL e Segurança de Domínios

- ✅ SSL 100% via Cloudflare (Universal SSL)
- ❌ Nenhum Certbot manual
- ❌ Nenhuma configuração por domínio no Nginx
- ✅ Nginx recebe apenas HTTPS válido do Cloudflare

**Fluxo:** Cliente → Cloudflare (HTTPS) → Nginx (HTTP interno) → Django

---

## Configuração do Nginx

### Características Principais

- `default_server` configurado
- Sem `server_name` fixo (aceita qualquer domínio)
- Proxy reverso para Django/Gunicorn
- Headers de segurança globais
- Rate limiting configurado

### Exemplo Mínimo

```nginx
server {
    listen 80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Segurança (Best Practices)

### Implementações Obrigatórias

- ✅ **HTTPS obrigatório** (via Cloudflare)
- ✅ **Cookies Secure + HttpOnly**
- ✅ **CSRF ativo** em todas as views
- ✅ **Rate limiting** no login e endpoints críticos
- ✅ **Allowed Hosts dinâmico** (validação por middleware)
- ✅ **Isolamento total por tenant** (queries sempre filtradas)
- ✅ **Bloqueio de hosts desconhecidos** (retorna 403)

### Headers de Segurança

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

---

## Celery (Processamento Assíncrono)

### Utilizado Para

- ✅ Verificação automática de domínios
- ✅ Envio de e-mails transacionais
- ✅ Processamento de imagens (thumbnails, otimização)
- ✅ Tarefas recorrentes (limpeza, relatórios)
- ✅ Limpeza de cache periódica

### Configuração

- **Broker:** Redis
- **Backend:** Redis
- **Beat:** Celery Beat para tarefas agendadas

**✅ Resultado:** Sem cron manual. Tudo gerenciado pelo Django/Celery.

---

## Internacionalização (i18n)

### Configuração Django

```python
# settings/base.py
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('pt-br', 'Português'),
    ('en', 'English'),
    ('es', 'Español'),
]

LANGUAGE_CODE = 'pt-br'
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### Middleware

```python
MIDDLEWARE = [
    # ...
    'django.middleware.locale.LocaleMiddleware',
    # ...
]
```

### Estrutura de Arquivos

```
locale/
├── pt_BR/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
├── en/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── es/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo
```

### Uso em Templates

```django
{% load i18n %}
<h1>{% trans "Dashboard" %}</h1>
<p>{% trans "Welcome back" %}</p>
```

### Uso em Python

```python
from django.utils.translation import gettext_lazy as _

message = _("User created successfully")
```

### Detecção de Idioma

O idioma pode ser definido por:

- **Tenant** (configuração padrão do cliente)
- **Usuário** (preferência pessoal)
- **Domínio** (baseado no país/região)
- **Cookie** (última escolha do usuário)

---

## Frontend com Bootstrap

### Princípios

- ✅ Layout base único e reutilizável
- ✅ Componentização de templates Django
- ✅ Navbar pública ≠ Navbar dashboard
- ✅ Sem CSS inline
- ✅ Sem JavaScript desnecessário
- ✅ Responsivo por padrão (mobile-first)

### Estrutura de Templates

```
templates/
├── base/
│   ├── base.html
│   ├── public_base.html
│   └── dashboard_base.html
├── components/
│   ├── navbar.html
│   ├── footer.html
│   └── sidebar.html
└── pages/
    ├── public/
    └── dashboard/
```

---

## Ferramentas Externas Utilizadas

### Obrigatórias

| Ferramenta | Uso |
|------------|-----|
| **Cloudflare** | DNS, SSL automático, WAF, CDN |
| **Docker** | Containerização da aplicação |
| **PostgreSQL** | Banco de dados principal |
| **Redis** | Cache e broker Celery |

### Recomendadas

| Ferramenta | Uso |
|------------|-----|
| **Sentry** | Monitoramento de erros em produção |
| **UptimeRobot** | Monitoramento de uptime |
| **Backup automático** | Backup diário do banco de dados |
| **MinIO** | Storage S3-compatible para arquivos |

---

## O Que NÃO É Utilizado

- ❌ Certbot manual
- ❌ VHosts por cliente no Nginx
- ❌ DNS manual no servidor
- ❌ Configuração manual de SSL por domínio
- ❌ Suporte humano para configuração de domínio
- ❌ Cron jobs manuais
- ❌ Deploy manual via SSH

**✅ Tudo é automatizado e gerenciado via código.**

---

## Princípios Seguidos

### Arquitetura

- ✅ **Clean Architecture** (separação de camadas)
- ✅ **Separation of Concerns** (responsabilidade única)
- ✅ **DRY** (Don't Repeat Yourself)
- ✅ **SOLID** (princípios de design)

### Segurança

- ✅ **Security by Design** (segurança desde o início)
- ✅ **Defense in Depth** (múltiplas camadas)
- ✅ **Least Privilege** (menor privilégio necessário)

### Operações

- ✅ **Infrastructure as Code** (Docker, scripts)
- ✅ **Zero Manual Operations** (tudo automatizado)
- ✅ **Escalabilidade Horizontal** (preparado para crescer)

---

## Fluxo de Requisição Completo

```
1. Cliente acessa: cliente.propzy.com.br
   ↓
2. Cloudflare (DNS + SSL)
   ↓
3. Nginx (proxy reverso)
   ↓
4. Middleware Tenant (identifica domínio)
   ↓
5. Django View (com request.tenant disponível)
   ↓
6. Query filtrada por tenant
   ↓
7. Resposta renderizada
   ↓
8. Cliente recebe página personalizada
```

---

## Conclusão

Esta arquitetura permite operar um SaaS profissional, seguro e escalável, com suporte a milhares de clientes, múltiplos domínios, deploy automático e manutenção mínima.

**Tudo nasce pronto para crescer.**

---

## Próximos Passos Sugeridos

- 🔧 Criar o repositório base (estrutura completa de diretórios)
- 🧠 Implementar o middleware de tenant
- 🔍 Criar a task Celery de verificação de domínio
- 🚀 Gerar docker-compose.yml completo e funcional
- 🌍 Configurar setup completo de i18n no Django
- 🔐 Implementar sistema de autenticação por email (sem username)
- 👥 Configurar grupos padrão do Django para permissões
- 📊 Criar dashboard administrativo base
- 📧 Configurar sistema de e-mails transacionais

