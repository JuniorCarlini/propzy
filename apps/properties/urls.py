"""
URLs do app Properties
"""

from django.urls import path

from apps.properties import views

app_name = "properties"

urlpatterns = [
    path("imoveis/", views.property_list, name="property_list"),
    path("imoveis/novo/", views.property_create, name="property_create"),
    path("imoveis/<int:pk>/editar/", views.property_update, name="property_update"),
    path("imoveis/<int:pk>/", views.property_detail, name="property_detail"),
    path("imoveis/<int:pk>/ativar/", views.property_toggle_active, name="property_toggle_active"),
    path("imoveis/<int:pk>/excluir/", views.property_delete, name="property_delete"),
    path("imoveis/<int:pk>/imagens/", views.property_images_list, name="property_images_list"),
    path("imoveis/<int:pk>/imagens/upload/", views.property_image_upload, name="property_image_upload"),
    path("imoveis/<int:pk>/imagens/<int:image_id>/deletar/", views.property_image_delete, name="property_image_delete"),
    path(
        "imoveis/<int:pk>/imagens/<int:image_id>/principal/",
        views.property_set_main_image,
        name="property_set_main_image",
    ),
]
