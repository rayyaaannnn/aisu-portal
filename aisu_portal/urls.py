from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect   # ADD THIS

from members import views               # ADD THIS if not present

urlpatterns = [
    path('', lambda request: redirect('/admin/')),  # homepage
    path('admin/', admin.site.urls),

    path('super-admin/', views.super_admin_dashboard, name='super_admin'),
    path('it/', views.it_dashboard, name='it_dashboard'),
    path('state/', views.state_dashboard, name='state_dashboard'),
    path('district/', views.district_dashboard, name='district_dashboard'),
]
