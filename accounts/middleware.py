from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.urls import resolve

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware that checks for a valid JWT token in the request headers
    and adds the authenticated user to the request.
    """
    
    def process_request(self, request):
        # Skip authentication for these paths
        exempt_paths = [
            '/api/auth/login/',
            '/api/auth/token/refresh/',
            '/api/auth/password-reset/request/',
            '/api/auth/password-reset/confirm/',
            '/admin/',
            '/api/auth/users/', # Only for POST (register)
            '/api/products/categories',
        ]
        
        # Skip middleware for exempt paths
        for path in exempt_paths:
            if request.path.startswith(path):
                if request.path == '/api/auth/users/' and request.method != 'POST':
                    # Continue with JWT auth for GET, PUT, DELETE on users
                    break
                return None
        
        # Skip authentication for non-API requests
        if not request.path.startswith('/api/'):
            return None
        
        try:
            match = resolve(request.path)
            view_func = match.func

            if hasattr(view_func, 'cls') and issubclass(view_func.cls, APIView):
                permission_classes = getattr(view_func.cls, 'permission_classes', [])
                if AllowAny in permission_classes:
                    return None
        except Exception:
            pass
            
        # Try to authenticate with JWT
        jwt_authenticator = JWTAuthentication()
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header:
                auth_token = auth_header.split(' ')[1]
                validated_token = jwt_authenticator.get_validated_token(auth_token)
                request.user = jwt_authenticator.get_user(validated_token)
                request._jwt_validated_token = validated_token
                return None
            else:
                return JsonResponse(
                    {"detail": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return JsonResponse(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            ) 