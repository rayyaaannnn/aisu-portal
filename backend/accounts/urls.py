from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import DesignationViewSet, UserInfoView

# Create router for viewsets
router = DefaultRouter()
router.register(r'designations', DesignationViewSet, basename='designation')

urlpatterns = [
    # API endpoints for Designation
    path('', include(router.urls)),
    
    # API endpoint for user info (role-based redirects)
    path('user-info/', UserInfoView.as_view(), name='user_info'),
    
    # Auth endpoints
    path('login/', views.api_login, name='api_login'),
    path('logout/', views.api_logout, name='api_logout'),
    path('redirect/', views.role_redirect, name='role_redirect'),

    # Password reset (API-driven)
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Dashboard endpoints
    path('dashboard-counts/', views.dashboard_counts, name='dashboard_counts'),
    path('system-status/', views.system_status, name='system_status'),
    
    # Profile endpoints
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # User management endpoints (super_admin only)
    path('users/', views.manage_users, name='manage_users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]
