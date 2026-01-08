"""
URLs do app Administration
"""
from django.urls import path

from apps.administration import views

app_name = "administration_panel"

urlpatterns = [
    # Dashboard (raiz e /admin-panel/)
    path("", views.dashboard, name="dashboard"),
    path("admin-panel/", views.dashboard, name="dashboard_alt"),  # Alternativa
    # Usuários
    path("admin-panel/usuarios/", views.user_list, name="user_list"),
    path("admin-panel/usuarios/novo/", views.user_create, name="user_create"),
    path("admin-panel/usuarios/<int:pk>/editar/", views.user_update, name="user_update"),
    path("admin-panel/usuarios/<int:pk>/excluir/", views.user_delete, name="user_delete"),
    # Grupos
    path("admin-panel/grupos/", views.group_list, name="group_list"),
    path("admin-panel/grupos/novo/", views.group_create, name="group_create"),
    path("admin-panel/grupos/<int:pk>/editar/", views.group_update, name="group_update"),
    path("admin-panel/grupos/<int:pk>/excluir/", views.group_delete, name="group_delete"),
]

