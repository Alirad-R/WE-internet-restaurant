# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (
    UserViewSet,
    CustomerProfileViewSet,
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserProfileView,
    AdminUserManagementViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', CustomerProfileViewSet)
router.register(r'admin/users', AdminUserManagementViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    # path('jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]