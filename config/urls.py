from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# URLs que NÃO precisam de prefixo de idioma (admin, API, etc.)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

# URLs que PRECISAM de prefixo de idioma (páginas do usuário)
# prefix_default_language=False: não adiciona prefixo para o idioma padrão (pt-br)
# Exemplo: /accounts/login/ redireciona para /pt-br/accounts/login/
urlpatterns += i18n_patterns(
    path("accounts/", include("allauth.urls")),
    path("gestao/", include("apps.accounts.urls")),
    path("landings/", include("apps.landings.urls")),  # Dashboard de landing pages
    path("", include("apps.main.urls")),
    prefix_default_language=False,
)

# Landing pages públicas (catch-all - DEVE SER A ÚLTIMA!)
# Não tem prefixo de idioma para funcionar com domínios/subdomínios personalizados
# O middleware TenantMiddleware detecta se é uma landing page válida
from apps.landings.views import landing_page_view

urlpatterns += [
    path("", landing_page_view, name="landing_page_public"),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
