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
urlpatterns += i18n_patterns(
    path("accounts/", include("allauth.urls")),  # Autenticação
    path("core/", include("apps.core.urls")),  # Funcionalidades core (toggle theme, etc)
    path("", include("apps.administration.urls")),  # Painel administrativo (raiz e /admin-panel/)
    path("landings/", include("apps.landings.urls")),  # Dashboard de sites
    path("properties/", include("apps.properties.urls")),  # Módulo de imóveis
    prefix_default_language=False,
)

# Sites públicos (DEVE SER ANTES DO CATCH-ALL!)
# Não tem prefixo de idioma para funcionar com domínios/subdomínios personalizados
# O middleware TenantMiddleware detecta se é um site válido
from apps.landings.views import properties_list, property_detail, site_view

urlpatterns += [
    # Páginas públicas do site (acessadas diretamente no domínio do site)
    path("imoveis/", properties_list, name="landings_properties_list"),
    path("imovel/<int:pk>/", property_detail, name="landings_property_detail"),
    # Site público (catch-all - DEVE SER A ÚLTIMA!)
    path("", site_view, name="site_public"),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
