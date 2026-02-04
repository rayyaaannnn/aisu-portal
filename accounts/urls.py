from django.urls import path
from . import views

urlpatterns = [
    path('super-admin/', views.super_admin_dashboard, name='super_admin'),
    path('it/', views.it_dashboard, name='it_dashboard'),
    path('state/', views.state_dashboard, name='state_dashboard'),
    path('district/', views.district_dashboard, name='district_dashboard'),
]

path('redirect/', views.role_redirect, name='role_redirect'),
