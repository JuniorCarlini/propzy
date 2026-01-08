"""
URLs do app Landings.
"""

from django.urls import path

from . import views

app_name = "landings"

urlpatterns = [
    # Dashboard (configuração)
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    path("dashboard/config/basic/", views.dashboard_config_basic, name="dashboard_config_basic"),
    path("dashboard/check-subdomain/", views.check_subdomain_availability, name="check_subdomain_availability"),
    path("dashboard/config/domain/", views.dashboard_config_domain, name="dashboard_config_domain"),
    path("dashboard/config/theme/", views.dashboard_config_theme, name="dashboard_config_theme"),
    path("dashboard/configuracoes-avancadas/", views.dashboard_advanced_config, name="dashboard_advanced_config"),
    path("dashboard/theme/<slug:theme_slug>/preview/", views.dashboard_theme_preview, name="theme_preview"),
    path("dashboard/section-config/<str:section_key>/", views.dashboard_section_config_form, name="section_config_form"),
    # Páginas públicas do site (também disponíveis via /landings/)
    path("imoveis/", views.properties_list, name="properties_list"),
    path("imovel/<int:pk>/", views.property_detail, name="property_detail"),
    # Site público (catch-all - será adicionada no urls.py principal)
    path("", views.site_view, name="view"),
]
