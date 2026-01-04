from django.urls import path

from apps.main.views import index_view, toggle_theme_view

app_name = "main"

urlpatterns = [
    path("", index_view, name="index"),
    path("toggle-theme/", toggle_theme_view, name="toggle_theme"),
]
