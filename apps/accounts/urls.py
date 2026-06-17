from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from apps.accounts.views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    AuthMeView,
    UserMeView,
    UserConsentViewSet
)

router = DefaultRouter()
router.register('consents', UserConsentViewSet, basename='user-consent')

urlpatterns = [
    # Authentication Endpoints
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', AuthMeView.as_view(), name='auth-me'),
    
    # User Endpoints
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('', include(router.urls)),
]

