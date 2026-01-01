from django.urls import path
from . import views

app_name = 'public_site'

urlpatterns = [
    path('', views.tenant_public_site, name='tenant_site'),
    path('landing/', views.landing_page, name='landing'),
]
