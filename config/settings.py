"""
Configurações Django para o projeto propzy.

Este arquivo centraliza todas as configurações do sistema, usando python-decouple
para leitura segura de variáveis de ambiente (.env). Mantém valores padrão para
desenvolvimento local, mas requer configuração adequada para produção.
"""

from pathlib import Path

from decouple import Csv, config
from django.utils.translation import gettext_lazy as _

# ============================================================================
# CONFIGURAÇÕES BÁSICAS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: mantenha a chave secreta usada em produção em segredo!
SECRET_KEY = config("SECRET_KEY", default="wv%0t#z=b&5@(1bpqh(i8ahgse9npgd&g#%huylyda1458jq31")

# SECURITY WARNING: não execute com debug=True em produção!
DEBUG = config("DEBUG", default=True, cast=bool)

# Hosts permitidos para servir a aplicação (obrigatório em produção)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# Origens confiáveis para proteção CSRF (necessário quando frontend está em domínio diferente)
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="http://localhost:3000", cast=Csv())


# ============================================================================
# APLICAÇÕES INSTALADAS
# ============================================================================

# Apps nativos do Django necessários para funcionalidades básicas
BASE_APPS = [
    "django.contrib.admin",  # Interface administrativa
    "django.contrib.auth",  # Sistema de autenticação
    "django.contrib.contenttypes",  # Framework de tipos de conteúdo
    "django.contrib.sessions",  # Framework de sessões
    "django.contrib.messages",  # Framework de mensagens
    "django.contrib.staticfiles",  # Gestão de arquivos estáticos
    "django.contrib.sites",  # Framework de sites (requerido pelo allauth)
]

# Bibliotecas de terceiros
THIRD_PARTY_APPS = [
    "allauth",  # Autenticação avançada (login por e-mail, OAuth, etc.)
    "allauth.account",  # Módulo de contas do allauth
    "crispy_forms",  # Renderização de formulários com Bootstrap
    "crispy_bootstrap5",  # Templates Bootstrap 5 para crispy-forms
    "django_celery_beat",  # Agendamento de tarefas periódicas do Celery
]

# Apps internos do projeto propzy
APP_APPS = [
    "apps.accounts",  # Gestão de usuários customizados, grupos e permissões
    "apps.main",  # Dashboard e páginas principais
    "apps.landings",  # Landing Pages Multi-tenant
]

INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + APP_APPS


# ============================================================================
# MIDDLEWARE (ordem importa!)
# ============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Segurança (HTTPS, headers, etc.)
    "django.contrib.sessions.middleware.SessionMiddleware",  # Gerencia sessões de usuários
    "django.middleware.locale.LocaleMiddleware",  # CUSTOMIZADO: Detecta idioma preferido do usuário
    "django.middleware.common.CommonMiddleware",  # Funcionalidades comuns (redirect, ETags, etc.)
    "apps.landings.middleware.TenantMiddleware",  # CUSTOMIZADO: Detecta tenant para multi-tenant
    "django.middleware.csrf.CsrfViewMiddleware",  # Proteção contra CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Associa usuário à request
    "allauth.account.middleware.AccountMiddleware",  # CUSTOMIZADO: Middleware do django-allauth
    "django.contrib.messages.middleware.MessageMiddleware",  # Sistema de mensagens (toasts, alertas)
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Proteção contra clickjacking
]


# ============================================================================
# TEMPLATES
# ============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # CUSTOMIZADO: Templates centralizados em /templates (não dentro de cada app)
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,  # Também busca em templates/ dentro de cada app instalado (Precisa para o crispy)
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # Necessário para allauth e crispy-forms
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================================
# URLS E WSGI
# ============================================================================

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# ============================================================================
# AUTENTICAÇÃO E PERMISSÕES
# ============================================================================

# CUSTOMIZADO: Usa modelo de usuário customizado que autentica via e-mail (sem username)
# O app_label é 'accounts' (definido no AppConfig.label), não 'apps.accounts'
AUTH_USER_MODEL = "accounts.User"

# Backends de autenticação (permite login via Django padrão + allauth)
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Backend padrão do Django
    "allauth.account.auth_backends.AuthenticationBackend",  # Backend do allauth
]

# SITE_ID é necessário pelo django-allauth (framework de sites)
SITE_ID = 1

# Redirecionamentos após login/logout
LOGIN_REDIRECT_URL = "main:index"
LOGOUT_REDIRECT_URL = "account_login"
LOGIN_URL = "account_login"

# Configurações do django-allauth (login apenas por e-mail, sem cadastro público)
ACCOUNT_ADAPTER = "apps.accounts.adapter.AccountAdapter"  # CUSTOMIZADO: Adapter que desabilita signup
ACCOUNT_EMAIL_VERIFICATION = "none"  # Não requer verificação de e-mail (usuários criados por admin)
ACCOUNT_LOGIN_METHODS = {"email"}  # CUSTOMIZADO: Login apenas por e-mail (sem username)
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",  # Limite de 5 tentativas falhas de login a cada 5 minutos
}
ACCOUNT_SESSION_REMEMBER = True  # "Lembrar acesso" marcado por padrão
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # CUSTOMIZADO: Não usa campo username
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[propzy] "
ACCOUNT_FORMS = {
    # CUSTOMIZADO: Formulários personalizados com crispy-forms e Bootstrap
    "login": "apps.accounts.forms.LoginForm",
    "reset_password": "apps.accounts.forms.ResetPasswordForm",
    "reset_password_from_key": "apps.accounts.forms.ResetPasswordKeyForm",
}

# Configuração do crispy-forms para usar Bootstrap 5
CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5",)
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ============================================================================
# BANCO DE DADOS
# ============================================================================

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": config("DB_NAME", default="propzy"),
        "USER": config("DB_USER", default="propzy"),
        "PASSWORD": config("DB_PASSWORD", default="propzy123"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 600,  # CUSTOMIZADO: Mantém conexões por 10min (pool de conexões)
        "OPTIONS": {
            "connect_timeout": 10,  # Timeout de conexão de 10 segundos
        },
    }
}


# ============================================================================
# CACHE E SESSÕES (Redis)
# ============================================================================

# Variáveis de conexão Redis (usado para cache, sessões e Celery)
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default="6379")
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")
REDIS_DB = config("REDIS_DB", default="0")

# Monta URL de conexão Redis (com ou sem senha)
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# CUSTOMIZADO: Cache via Redis (melhor performance que cache em banco)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "propzy",  # Prefixo para evitar conflito se Redis for compartilhado
        "TIMEOUT": 300,  # Timeout padrão de 5 minutos
    }
}

# CUSTOMIZADO: Sessões armazenadas no Redis (não no banco de dados)
# Benefícios: melhor performance, menor carga no PostgreSQL
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# ============================================================================
# VALIDAÇÃO DE SENHAS
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================================================================
# INTERNACIONALIZAÇÃO (i18n)
# ============================================================================

# CUSTOMIZADO: Idioma padrão brasileiro, mas suporta inglês via seletor no menu
LANGUAGE_CODE = config("LANGUAGE_CODE", default="pt-br")

# Idiomas disponíveis no sistema (aparecem no seletor de idioma)
LANGUAGES = (
    ("pt-br", _("Português")),
    ("en", _("English")),
    ("es", _("Español")),
)

# CUSTOMIZADO: Diretório onde ficam os catálogos de tradução (.po/.mo)
LOCALE_PATHS = [BASE_DIR / "locale"]

# Fuso horário padrão (Rondônia/Brasil)
TIME_ZONE = config("TIME_ZONE", default="America/Porto_Velho")

# Habilita internacionalização (tradução de strings)
USE_I18N = config("USE_I18N", default=True, cast=bool)

# Usa fuso horário (armazena datas em UTC, exibe no fuso configurado)
USE_TZ = config("USE_TZ", default=True, cast=bool)


# ============================================================================
# CELERY (Tarefas Assíncronas)
# ============================================================================

# CUSTOMIZADO: Configuração do Celery para processar tarefas em background
# Usa Redis como broker (fila de mensagens) e backend (armazenamento de resultados)
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Configurações de serialização (usa JSON para melhor compatibilidade)
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Configurações de timezone (usa o mesmo timezone do Django)
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = USE_TZ

# Configurações de workers
CELERY_WORKER_CONCURRENCY = config("CELERY_WORKER_CONCURRENCY", default=4, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config("CELERY_WORKER_MAX_TASKS_PER_CHILD", default=1000, cast=int)
CELERY_WORKER_PREFETCH_MULTIPLIER = config("CELERY_WORKER_PREFETCH_MULTIPLIER", default=4, cast=int)

# Configurações de tarefas
CELERY_TASK_ACKS_LATE = True  # Confirma tarefa apenas após conclusão bem-sucedida
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # Rejeita tarefas se worker morrer
CELERY_TASK_TIME_LIMIT = config("CELERY_TASK_TIME_LIMIT", default=300, cast=int)  # Timeout de 5 minutos
CELERY_TASK_SOFT_TIME_LIMIT = config("CELERY_TASK_SOFT_TIME_LIMIT", default=240, cast=int)  # Soft timeout de 4 minutos
CELERY_TASK_TRACK_STARTED = True  # Rastreia quando a tarefa começa

# Configurações de retry
CELERY_TASK_DEFAULT_RETRY_DELAY = config("CELERY_TASK_DEFAULT_RETRY_DELAY", default=60, cast=int)  # 1 minuto
CELERY_TASK_MAX_RETRIES = config("CELERY_TASK_MAX_RETRIES", default=3, cast=int)

# Configurações de resultados
CELERY_RESULT_EXPIRES = config("CELERY_RESULT_EXPIRES", default=3600, cast=int)  # Expira após 1 hora
CELERY_RESULT_EXTENDED = True  # Armazena metadados adicionais dos resultados

# Configurações de filas (opcional - pode criar filas específicas depois)
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_DEFAULT_EXCHANGE = "default"
CELERY_TASK_DEFAULT_ROUTING_KEY = "default"

# Configurações de beat (para tarefas agendadas)
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# ============================================================================
# ARQUIVOS ESTÁTICOS (CSS, JavaScript, Images)
# ============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Diretório onde collectstatic reúne todos os arquivos
STATICFILES_DIRS = [
    BASE_DIR / "static",  # CUSTOMIZADO: Arquivos estáticos globais do projeto (logo, etc.)
]

# Arquivos de upload dos usuários
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================================================================
# AWS S3 (Armazenamento em Nuvem - Opcional)
# ============================================================================

# CUSTOMIZADO: Se USE_S3=True, usa S3 para armazenar estáticos e media (não sistema de arquivos local)
USE_S3 = config("USE_S3", default=False, cast=bool)

if USE_S3:
    # Credenciais e configuração do bucket S3
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", default=f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com")
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",  # Cache de 24 horas no navegador
    }
    AWS_DEFAULT_ACL = "public-read"  # Arquivos públicos por padrão
    AWS_LOCATION = "static"

    # Usa S3 para arquivos estáticos
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

    # Usa S3 para arquivos de upload (media)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"


# ============================================================================
# ENVIO DE E-MAILS
# ============================================================================

EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@propzy.local")


# ============================================================================
# SEGURANÇA (aplicado apenas em produção, quando DEBUG=False)
# ============================================================================

if not DEBUG:
    # CUSTOMIZADO: Configurações de segurança para ambiente de produção
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)  # Redireciona HTTP -> HTTPS
    SESSION_COOKIE_SECURE = config(
        "SESSION_COOKIE_SECURE", default=True, cast=bool
    )  # Cookie de sessão apenas via HTTPS
    CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)  # Cookie CSRF apenas via HTTPS
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)  # HSTS por 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True, cast=bool
    )  # HSTS em subdomínios
    SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=True, cast=bool)  # HSTS preload
    SECURE_BROWSER_XSS_FILTER = True  # Proteção XSS no navegador
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Previne MIME-sniffing
    X_FRAME_OPTIONS = "DENY"  # Previne clickjacking

    # CUSTOMIZADO: Confia no header X-Forwarded-Proto do proxy reverso (NGINX/Cloudflare)
    # Necessário para evitar loop de redirect quando o Cloudflare/NGINX já fornecem HTTPS
    USE_X_FORWARDED_HOST = config("USE_X_FORWARDED_HOST", default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = config("LOG_LEVEL", default="INFO")

# CUSTOMIZADO: Logging adaptado para produção vs desenvolvimento
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            # CUSTOMIZADO: Em produção, não loga queries SQL (WARNING only)
            "level": "WARNING" if not DEBUG else "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            # CUSTOMIZADO: Em produção, não loga cada tarefa executada (WARNING only)
            "level": "WARNING" if not DEBUG else "INFO",
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["console"],
            "level": "WARNING" if not DEBUG else "INFO",
            "propagate": False,
        },
    },
}


# ============================================================================
# OUTROS
# ============================================================================

# Tipo de chave primária padrão para novos modelos
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================================
# MULTI-TENANT / LANDING PAGES
# ============================================================================

# Domínio base do sistema (usado para detectar subdomínios)
BASE_DOMAIN = config("BASE_DOMAIN", default="propzy.com.br")

# ALLOWED_HOSTS deve incluir o domínio base e seus subdomínios (wildcard)
# Em produção, configure: ALLOWED_HOSTS=.propzy.com.br,propzy.com.br
# O ponto antes do domínio permite todos os subdomínios
