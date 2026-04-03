from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('super-admin/', views.super_admin_dashboard, name='super_admin'),
    path('it/', views.it_dashboard, name='it_dashboard'),
    path('state/', views.state_dashboard, name='state_dashboard'),
    path('district/', views.district_dashboard, name='district_dashboard'),
    path('dashboard-counts/', views.dashboard_counts, name='dashboard_counts'),
    path('users/', views.manage_users, name='manage_users'),
        path('profile/', views.profile_view, name='profile'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]
