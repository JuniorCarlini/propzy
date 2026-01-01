from django.urls import path
from . import views

app_name = 'domains'

urlpatterns = [
    path('', views.domain_list, name='list'),
    path('create/', views.domain_create, name='create'),
    path('<uuid:domain_id>/', views.domain_detail, name='detail'),
    path('<uuid:domain_id>/verify/', views.domain_verify, name='verify'),
]



