"""
URLs do app Landings.
"""

from django.urls import path

from . import views

app_name = "landings"

urlpatterns = [
    # Dashboard (configuração)
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    path("dashboard/config/", views.dashboard_config, name="dashboard_config"),
    path("dashboard/theme/<slug:theme_slug>/preview/", views.dashboard_theme_preview, name="theme_preview"),
    # Landing page pública (catch-all - será adicionada no urls.py principal)
    path("", views.landing_page_view, name="view"),
]



