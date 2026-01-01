"""
URL configuration for propzy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# URLs com suporte a i18n
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('dashboard/domains/', include('apps.domains.urls')),
)

# API sem i18n (não precisa de tradução)
urlpatterns += [
    path('api/', include('apps.common.urls')),
]

# URLs públicas (sem i18n para facilitar)
urlpatterns += [
    path('', include('apps.public_site.urls')),
]

# Media files (apenas em desenvolvimento)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
