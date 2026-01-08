"""
URLs do app Core
"""

from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("toggle-theme/", views.toggle_theme, name="toggle_theme"),
    path("perfil/", views.profile, name="profile"),
    path("perfil/senha/", views.profile_password, name="profile_password"),
    path("onboarding/dismiss-completion/", views.dismiss_onboarding_completion, name="dismiss_onboarding_completion"),
]
