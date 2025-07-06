# accounts/views.py
import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, User, CustomerProfile
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserWithProfileSerializer,
    CustomerProfileSerializer,
    CustomerProfileUpdateSerializer,
)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve_with_profile':
            return UserWithProfileSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"detail": "User successfully deactivated."}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def retrieve_with_profile(self, request, pk=None):
        """
        Retrieve a user with their customer profile
        """
        user = self.get_object()
        serializer = UserWithProfileSerializer(user)
        return Response(serializer.data)

class CustomerProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CustomerProfile CRUD operations
    """
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = []
    
    def get_queryset(self):
        # Users can only see their own profile
        return CustomerProfile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CustomerProfileUpdateSerializer
        return CustomerProfileSerializer
    
    def list(self, request):
        # Return only the user's own profile
        profile = self.get_queryset().first()
        if profile:
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get the current user's profile
        """
        profile = self.get_queryset().first()
        if profile:
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Generate OTP
                otp_code = ''.join(random.choices(string.digits, k=6))
                
                # Save OTP to database
                OTP.objects.filter(user=user, is_used=False).update(is_used=True)  # Invalidate previous OTPs
                OTP.objects.create(user=user, otp_code=otp_code)
                
                # Send email with OTP
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp_code}. It will expire in 10 minutes.',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
                
                return Response({"message": "OTP has been sent to your email."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # For security reasons, don't reveal that the email doesn't exist
                return Response({"message": "If this email exists in our system, an OTP has been sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = User.objects.get(email=email)
                otp = OTP.objects.filter(
                    user=user,
                    otp_code=otp_code,
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).first()
                
                if otp:
                    # Set new password
                    user.set_password(new_password)
                    user.save()
                    
                    # Mark OTP as used
                    otp.is_used = True
                    otp.save()
                    
                    return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = []
    
    def get(self, request):
        """
        Get current user's profile with customer profile data
        """
        user = request.user
        serializer = UserWithProfileSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        """
        Update both user and customer profile data
        """
        user = request.user
        user_data = {}
        profile_data = {}
        
        # Separate user and profile data
        for key, value in request.data.items():
            if key in UserUpdateSerializer.Meta.fields:
                user_data[key] = value
            elif key in CustomerProfileUpdateSerializer.Meta.fields:
                profile_data[key] = value
        
        # Use transaction to ensure atomicity of updates
        with transaction.atomic():
            # Update user data if provided
            if user_data:
                user_serializer = UserUpdateSerializer(user, data=user_data, partial=True, context={'request': request})
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Update profile data if provided
            if profile_data:
                try:
                    profile = user.customer_profile
                except CustomerProfile.DoesNotExist:
                    profile = CustomerProfile.objects.create(user=user)
                
                profile_serializer = CustomerProfileUpdateSerializer(profile, data=profile_data, partial=True)
                if profile_serializer.is_valid():
                    profile_serializer.save()
                else:
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Return updated user with profile
        result_serializer = UserWithProfileSerializer(user)
        return Response(result_serializer.data)