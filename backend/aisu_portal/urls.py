from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def api_root(request):
    return JsonResponse({
        'message': 'AISU Portal API',
        'status': 'running',
        'endpoints': {
            'login': '/api/token/',
            'refresh_token': '/api/token/refresh/',
            'accounts_api': '/accounts/',
            'admin': '/admin/'
        },
        'frontend': 'http://localhost:3000'
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]

