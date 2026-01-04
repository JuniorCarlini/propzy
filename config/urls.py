from django.conf.urls.i18n import i18n_patterns
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
    path("", include("apps.main.urls")),
    prefix_default_language=False,
)
