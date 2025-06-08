# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (
    UserViewSet,
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserProfileView,
    CustomerProfileViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'customer-profiles', CustomerProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]