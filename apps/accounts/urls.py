from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("usuarios/", views.user_list, name="user_list"),
    path("usuarios/novo/", views.user_create, name="user_create"),
    path("usuarios/<int:pk>/editar/", views.user_update, name="user_update"),
    path("usuarios/<int:pk>/excluir/", views.user_delete, name="user_delete"),
    path("grupos/", views.group_list, name="group_list"),
    path("grupos/novo/", views.group_create, name="group_create"),
    path("grupos/<int:pk>/editar/", views.group_update, name="group_update"),
    path("grupos/<int:pk>/excluir/", views.group_delete, name="group_delete"),
]
