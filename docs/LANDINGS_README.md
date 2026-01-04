# 🏠 Sistema Multi-Tenant de Landing Pages - Propzy

Sistema completo de Landing Pages multi-tenant para corretores e imobiliárias, com suporte a subdomínios automáticos e domínios personalizados.

## 📋 Índice

- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Temas](#temas)
- [Uso](#uso)
- [Deploy em Produção](#deploy-em-produção)

---

## ✨ Funcionalidades

### Para Corretores/Imobiliárias
- ✅ Landing page personalizada automática
- ✅ Subdomínio exclusivo: `usuario.propzy.com.br`
- ✅ Domínio personalizado: `www.minhaempresa.com.br`
- ✅ Múltiplos temas profissionais (Modern, Classic, Minimal)
- ✅ Cadastro de imóveis com galeria de fotos
- ✅ Integração com WhatsApp
- ✅ Personalização de cores
- ✅ SEO otimizado

### Para Administradores
- ✅ Gestão completa via Django Admin
- ✅ Sistema de temas em pastas
- ✅ Fácil adicionar novos temas
- ✅ Multi-tenant automático via middleware
- ✅ 100% automatizado (zero configuração manual por usuário)

---

## 🏗️ Arquitetura

```
Internet → Cloudflare → NGINX (Proxy Reverso) → Django Multi-Tenant

Fluxo:
1. Requisição chega com host: fulano.propzy.com.br
2. NGINX repassa para Django com header Host
3. TenantMiddleware detecta o tenant (Landing Page)
4. View renderiza o tema correto com dados do tenant
```

### Estrutura de Arquivos

```
apps/
└── landings/
    ├── models.py           # LandingPage, Property, LandingPageTheme
    ├── middleware.py       # TenantMiddleware (detecta tenant)
    ├── views.py            # Views públicas e dashboard
    ├── admin.py            # Admin completo
    ├── theme_manager.py    # Gerenciador de temas
    └── management/
        └── commands/
            └── install_themes.py

templates/
└── landings/
    ├── base_landing.html
    ├── _components/
    │   ├── property_card.html
    │   └── contact_section.html
    └── themes/
        ├── modern/
        │   ├── theme.json
        │   └── index.html
        ├── classic/
        ├── minimal/
        └── default/
```

---

## 🚀 Instalação

### 1. Instalar Dependências

```bash
# O Pillow já foi adicionado ao pyproject.toml
uv sync
```

### 2. Aplicar Migrações

```bash
python manage.py makemigrations landings
python manage.py migrate
```

### 3. Instalar Temas

```bash
# Instalar todos os temas disponíveis
python manage.py install_themes

# Ou instalar tema específico
python manage.py install_themes modern

# Listar temas disponíveis
python manage.py install_themes --scan

# Validar temas
python manage.py install_themes --validate
```

### 4. Criar Diretório de Media

```bash
mkdir -p media/logos media/heroes media/properties media/themes
```

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente (.env)

Adicione ao seu arquivo `.env`:

```bash
# Domínio base do sistema
BASE_DOMAIN=propzy.com.br

# ALLOWED_HOSTS deve incluir wildcards para subdomínios
# O ponto antes do domínio permite todos os subdomínios
ALLOWED_HOSTS=localhost,127.0.0.1,.propzy.com.br,propzy.com.br

# CSRF também precisa aceitar subdomínios
CSRF_TRUSTED_ORIGINS=https://.propzy.com.br,https://propzy.com.br,http://localhost
```

### 2. NGINX - Proxy Reverso (Produção)

Crie `/etc/nginx/sites-available/propzy`:

```nginx
# Upstream para Django
upstream django_app {
    server localhost:8000;
}

# Catch-all para todos os domínios e subdomínios
server {
    listen 80;
    server_name *.propzy.com.br propzy.com.br;

    # Redireciona HTTP para HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name *.propzy.com.br propzy.com.br;

    # Certificados SSL (use Certbot para gerar)
    ssl_certificate /etc/letsencrypt/live/propzy.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/propzy.com.br/privkey.pem;

    client_max_body_size 100M;

    # Arquivos estáticos
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
    }

    # Arquivos de mídia
    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    # Proxy para Django
    location / {
        proxy_pass http://django_app;

        # CRÍTICO: Passa o host original
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        proxy_redirect off;
    }
}
```

### 3. Cloudflare - DNS

#### Para Subdomínios Automáticos

```
Tipo: A ou CNAME
Nome: *
Conteúdo: IP_DO_SERVIDOR ou propzy.com.br
Proxy: ✅ Ativado
TTL: Auto
```

#### Para Domínios Personalizados (Cliente configura)

O cliente adiciona no DNS dele:

```
Tipo: CNAME
Nome: www (ou @)
Conteúdo: propzy.com.br
Proxy: ✅ Ativado (se usar Cloudflare)
```

### 4. SSL - Certificado Wildcard

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado wildcard (requer validação DNS)
sudo certbot certonly --manual --preferred-challenges dns \
  -d propzy.com.br -d *.propzy.com.br

# Renovação automática
sudo certbot renew --dry-run
```

---

## 🎨 Temas

### Temas Incluídos

1. **Modern** - Design moderno com animações suaves
2. **Classic** - Elegante e tradicional
3. **Minimal** - Minimalista e limpo
4. **Default** - Fallback básico

### Criar Novo Tema

1. **Criar estrutura:**

```bash
mkdir -p templates/landings/themes/meu-tema/static/css
mkdir -p templates/landings/themes/meu-tema/static/js
```

2. **Criar theme.json:**

```json
{
  "name": "Meu Tema",
  "slug": "meu-tema",
  "version": "1.0.0",
  "author": "Seu Nome",
  "description": "Descrição do tema",
  "category": "modern",
  "colors": {
    "primary": "#007bff",
    "secondary": "#6c757d"
  },
  "features": ["whatsapp_integration", "property_gallery"],
  "premium": false
}
```

3. **Criar index.html:**

```django
{% extends "landings/base_landing.html" %}
{% load static i18n %}

{% block content %}
<!-- Seu conteúdo aqui -->
<!-- Acesso aos dados via: {{ landing_page }}, {{ properties }}, {{ featured_properties }} -->
{% endblock %}
```

4. **Instalar o tema:**

```bash
python manage.py install_themes meu-tema
```

---

## 📖 Uso

### 1. Criar Usuário Admin

```bash
python manage.py createsuperuser
```

### 2. Acessar Admin

```
http://localhost:8000/admin/
```

### 3. Criar Landing Page

**Opção A: Automático**
- Usuário faz login no sistema
- Acessa `/landings/dashboard/`
- Sistema cria automaticamente a landing page

**Opção B: Manual no Admin**
- Admin > Landings > Landing Pages > Adicionar
- Preencher dados do corretor/imobiliária
- Definir subdomínio (ex: `joao`)
- Selecionar tema
- Marcar como "Publicada"

### 4. Adicionar Imóveis

- Admin > Landings > Imóveis > Adicionar
- Selecionar a Landing Page
- Preencher dados do imóvel
- Upload de fotos
- Marcar como "Ativo"
- Opcionalmente: "Destaque"

### 5. Acessar Landing Page

```
# Subdomínio
https://joao.propzy.com.br

# Domínio personalizado (após configurar DNS)
https://www.imobiliariasjoao.com.br
```

---

## 🌐 Deploy em Produção

### 1. Docker Compose (Recomendado)

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - app
    restart: unless-stopped

  app:
    build: .
    expose:
      - "8000"
    env_file:
      - .env
    volumes:
      - ./media:/app/media
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:17-alpine
    env_file:
      - .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2. Checklist de Produção

- [ ] `DEBUG=False` no `.env`
- [ ] `SECRET_KEY` segura e única
- [ ] `ALLOWED_HOSTS` configurado com wildcard
- [ ] `CSRF_TRUSTED_ORIGINS` configurado
- [ ] SSL/HTTPS ativado
- [ ] Certificado wildcard instalado
- [ ] DNS wildcard configurado
- [ ] `python manage.py collectstatic`
- [ ] `python manage.py migrate`
- [ ] `python manage.py install_themes`
- [ ] Backup automático do banco
- [ ] Monitoring (Sentry, etc)

---

## 🔧 Troubleshooting

### Landing page não aparece

**Sintoma:** Acesso ao subdomínio retorna 404

**Verificar:**
1. Landing Page está marcada como "Publicada"?
2. Landing Page está marcada como "Ativa"?
3. NGINX está passando o header `Host` corretamente?
4. Middleware `TenantMiddleware` está ativo no `settings.py`?

**Debug:**
```python
# Adicione no início da view landing_page_view
print(f"Host: {request.get_host()}")
print(f"Is Landing Page: {request.is_landing_page}")
print(f"Tenant: {request.tenant}")
```

### Imagens não carregam

**Verificar:**
1. Diretório `media/` existe e tem permissões corretas?
2. `MEDIA_URL` e `MEDIA_ROOT` configurados?
3. NGINX servindo `/media/` corretamente?

### Subdomínio não resolve

**Verificar:**
1. DNS wildcard `*.propzy.com.br` configurado?
2. Aguardar propagação DNS (até 48h)
3. Testar com: `nslookup teste.propzy.com.br`

---

## 📚 Documentação Adicional

### Models

- **LandingPageTheme**: Temas disponíveis no sistema
- **LandingPage**: Landing page de cada usuário
- **Property**: Imóveis da landing page
- **PropertyImage**: Galeria de imagens do imóvel

### Middleware

- **TenantMiddleware**: Detecta qual landing page servir baseado no host

### Management Commands

```bash
# Instalar temas
python manage.py install_themes

# Listar temas
python manage.py install_themes --scan

# Validar temas
python manage.py install_themes --validate
```

---

## 🤝 Contribuindo

Para adicionar novos temas, basta:
1. Criar pasta em `templates/landings/themes/`
2. Adicionar `theme.json` e `index.html`
3. Executar `python manage.py install_themes`

---

## 📝 Licença

Este projeto faz parte do sistema Propzy.

---

## 🆘 Suporte

Para dúvidas e suporte, entre em contato com a equipe de desenvolvimento.

**Bom uso! 🚀**



